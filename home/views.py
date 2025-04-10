from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django import forms
from .models import Candidate, Criteria, Event, Score
from django.contrib.auth.models import User, Group
from .forms import JudgeCreationForm
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Avg
from django.contrib import messages
from .forms import EventForm, JudgeForm, CriteriaForm, CandidateForm
from django.http import HttpResponse
from django.template.loader import render_to_string


# Check if user is Admin
def is_admin(user: User) -> bool:
    return user.is_superuser


# Check if user is Judge
def is_judge(user: User) -> bool:
    return not user.is_superuser


@login_required
def profile(request):
    return render(request, "profile.html", {"user": request.user})


@login_required
def dashboard(request):
    if is_admin(request.user):
        events = Event.objects.filter(created_by=request.user)
        return render(
            request,
            "home/admin_dashboard.html",
            {"events": events},
        )
    elif is_judge(request.user):
        events = Event.objects.filter(judges=request.user)
        return render(
            request,
            'home/judge_dashboard.html', 
            {"events": events},
        )
    return redirect("login")


@login_required
@user_passes_test(is_admin, login_url="dashboard")
def event_create(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            form.save_m2m()  # Save the many-to-many judges field
            return redirect("event_list") 
    else:
        form = EventForm()

    # Fetch all judges from the database
    judges = User.objects.filter(is_superuser=False)
    response = render(
        request,
        "home/event_create.html",
        {
            "form": form,
            "judges": judges,
        },
    )
    response['Content-Language'] = 'en'
    return response


@login_required
def event_list(request):
    query = request.GET.get("q", "")
    events = Event.objects.filter(
        Q(title__icontains=query) | Q(venue__icontains=query)
    ).order_by("-created_at")
    
    if is_admin(request.user):
        events = events.filter(created_by=request.user)
    elif is_judge(request.user):
        events = events.filter(judges=request.user)
        
    paginator = Paginator(events, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if request.headers.get("HX-Request"):  # Check if request is from HTMX
        html = render_to_string(
            "partials/event_list_table.html", {"page_obj": page_obj, "query": query}
        )
        return HttpResponse(html)  # Return only the table

    return render(
        request, "home/event_list.html", {"page_obj": page_obj, "query": query}
    )

@login_required
@user_passes_test(is_admin, login_url="dashboard")
def event_edit(request, event_id=None):
    if event_id:
        event = get_object_or_404(Event, id=event_id)
        form = EventForm(request.POST or None, instance=event)
    else:
        event = None
        form = EventForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            event_instance = form.save(commit=False)
            if not event:  # New event
                event_instance.created_by = request.user
            event_instance.save()
            form.save_m2m()  # Save ManyToMany relationships
            return redirect("event_list")

    judges = User.objects.filter(is_superuser=False)

    return render(
        request,
        "home/event_edit.html",
        {
            "form": form,
            "event": event,
            "judges": judges,
        },
    )


@login_required
def event_delete(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return redirect("event_list")

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Get candidates ordered by position
    candidates = event.candidates.all().order_by('position')
    
    # Get criteria for the event, split by round
    preliminary_criteria = event.criteria.filter(round="Preliminary")
    final_criteria = event.criteria.filter(round="Final")
    
    # Get judges for the event
    judges = event.judges.all()
    
    # Handle Candidate Form (Add/Edit)
    candidate_form = CandidateForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and 'add_candidate' in request.POST:
        if candidate_form.is_valid():
            candidate = candidate_form.save(commit=False)
            candidate.created_by = request.user
            candidate.event = event
            candidate.save()
            messages.success(request, "Candidate added successfully!")
            return redirect('event_detail', event_id=event.id)
    
    # Handle Candidate Edit
    if request.method == "POST" and 'edit_candidate' in request.POST:
        candidate_id = request.POST.get('candidate_id')
        candidate = get_object_or_404(Candidate, id=candidate_id, event=event)
        candidate_form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if candidate_form.is_valid():
            candidate_form.save()
            messages.success(request, "Candidate updated successfully!")
            return redirect('event_detail', event_id=event.id)
    
    # Handle Candidate Delete
    if request.method == "POST" and 'delete_candidate' in request.POST:
        candidate_id = request.POST.get('candidate_id')
        candidate = get_object_or_404(Candidate, id=candidate_id, event=event)
        candidate.delete()
        messages.success(request, "Candidate deleted successfully!")
        return redirect('event_detail', event_id=event.id)
    
    # Handle Criteria Form (Add/Edit)
    criteria_form = CriteriaForm(request.POST or None)
    if request.method == "POST" and 'add_criteria' in request.POST:
        if criteria_form.is_valid():
            criteria = criteria_form.save(commit=False)
            criteria.created_by = request.user
            criteria.event = event
            criteria.save()
            messages.success(request, "Criteria added successfully!")
            return redirect('event_detail', event_id=event.id)
    
    # Handle Criteria Edit
    if request.method == "POST" and 'edit_criteria' in request.POST:
        criteria_id = request.POST.get('criteria_id')
        criteria = get_object_or_404(Criteria, id=criteria_id, event=event)
        criteria_form = CriteriaForm(request.POST, instance=criteria)
        if criteria_form.is_valid():
            criteria_form.save()
            messages.success(request, "Criteria updated successfully!")
            return redirect('event_detail', event_id=event.id)
    
    # Handle Criteria Delete
    if request.method == "POST" and 'delete_criteria' in request.POST:
        criteria_id = request.POST.get('criteria_id')
        criteria = get_object_or_404(Criteria, id=criteria_id, event=event)
        criteria.delete()
        messages.success(request, "Criteria deleted successfully!")
        return redirect('event_detail', event_id=event.id)
    
    context = {
        'event': event,
        'candidates': candidates,
        'preliminary_criteria': preliminary_criteria,
        'final_criteria': final_criteria,
        'judges': judges,
        'candidate_form': candidate_form,
        'criteria_form': criteria_form,
    }
    return render(request, 'home/event_detail.html', context)


# Judge Views
@login_required
def judge_list(request):
    query = request.GET.get("q", "")
    judges = User.objects.filter(Q(username__icontains=query)&Q(is_superuser=False)).order_by("username")
    if is_admin(request.user):
        judges = judges.filter(groups__name="Judge")
    paginator = Paginator(judges, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    if request.headers.get("HX-Request"):  # Check if request is from HTMX
        html = render_to_string(
            "partials/judge_list_table.html", {"page_obj": page_obj, "query": query}
        )
        return HttpResponse(html)
    
    return render(
        request, "home/judge_list.html", {"page_obj": page_obj, "query": query}
    )


@login_required
def judge_create(request):
    if request.method == "POST":
        form = JudgeCreationForm(request.POST)
        if form.is_valid():
            form.save() 
            return redirect("judge_list")
    else:
        form = JudgeCreationForm()
    return render(request, "home/judge_create.html", {"form": form})


@login_required
def judge_edit(request, id):
    judge = get_object_or_404(User, id=id)
    form = JudgeForm(request.POST or None, instance=judge)

    if request.method == "POST":
        if form.is_valid():
            try:
                form.save()
                return redirect("judge_list")
            except forms.ValidationError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, "home/judge_edit.html", {"form": form, "judge": judge})

@login_required
def judge_delete(request, id):
    judge = get_object_or_404(User, id=id)
    judge.delete()
    return redirect("judge_list")


@login_required
def event_judge_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    query = request.GET.get("q", "")
    judges = event.judges.filter(Q(username__icontains=query))
    paginator = Paginator(judges, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "home/judge_list.html",
        {"page_obj": page_obj, "query": query, "event": event},
    )


@login_required
def event_judge_add(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == "POST":
        judge_ids = request.POST.getlist("judges")
        event.judges.add(*judge_ids)
        messages.success(request, "Judges added successfully!")
        return redirect("event_judge_list", event_id=event_id)
    judges = User.objects.exclude(id__in=event.judges.all())
    return render(request, "home/judge_create.html", {"event": event, "judges": judges})


@login_required
def event_judge_delete(request, event_id, judge_id):
    event = get_object_or_404(Event, id=event_id)
    judge = get_object_or_404(User, id=judge_id)
    event.judges.remove(judge)
    messages.success(request, "Judge removed successfully!")
    return redirect("event_judge_list", event_id=event_id)


# Admin: Add Candidate
@login_required
@user_passes_test(is_admin)
def add_candidate(request):
    if request.method == "POST":
        name = request.POST["name"]
        gender = request.POST["gender"]
        picture = request.FILES.get("picture")
        Candidate.objects.create(
            name=name, gender=gender, picture=picture, created_by=request.user
        )
        return redirect("dashboard")
    return render(request, "home/add_candidate.html")


# Admin: Edit Candidate
@login_required
@user_passes_test(is_admin)
def edit_candidate(request, id):
    candidate = get_object_or_404(Candidate, id=id, created_by=request.user)
    if request.method == "POST":
        candidate.name = request.POST["name"]
        candidate.gender = request.POST["gender"]
        if request.FILES.get("picture"):
            candidate.picture = request.FILES["picture"]
        candidate.save()
        return redirect("dashboard")
    return render(request, "home/edit_candidate.html", {"candidate": candidate})


# Admin: Delete Candidate
@login_required
@user_passes_test(is_admin)
def delete_candidate(request, id):
    candidate = get_object_or_404(Candidate, id=id, created_by=request.user)
    if request.method == "POST":  # Confirm deletion via POST
        candidate.delete()
        return redirect("dashboard")
    return render(request, "home/delete_candidate.html", {"candidate": candidate})


# Criteria Views
@login_required
def criteria_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    criterias = Criteria.objects.filter(event=event)
    return render(
        request,
        "criterias/criteria_list.html",
        {"event": event, "criterias": criterias},
    )


# Admin: Add Criteria
@login_required
def criteria_add(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == "POST":
        form = CriteriaForm(request.POST)
        if form.is_valid():
            criteria = form.save(commit=False)
            criteria.event = event
            criteria.created_by = request.user
            criteria.save()
            messages.success(request, "Criteria added successfully!")
            return redirect("criteria_list", event_id=event_id)
    else:
        form = CriteriaForm()
    return render(
        request, "criterias/criteria_list.html", {"form": form, "event": event}
    )


# Admin: Edit Criteria
@login_required
def criteria_edit(request, event_id, criteria_id):
    event = get_object_or_404(Event, id=event_id)
    criteria = get_object_or_404(Criteria, id=criteria_id)
    if request.method == "POST":
        form = CriteriaForm(request.POST, instance=criteria)
        if form.is_valid():
            form.save()
            messages.success(request, "Criteria updated successfully!")
            return redirect("criteria_list", event_id=event_id)
    else:
        form = CriteriaForm(instance=criteria)
    return render(
        request,
        "criterias/criteria_list.html",
        {"form": form, "event": event, "criteria": criteria},
    )


# Admin: Delete Criteria
@login_required
def criteria_delete(request, event_id, criteria_id):
    criteria = get_object_or_404(Criteria, id=criteria_id)
    criteria.delete()
    messages.success(request, "Criteria deleted successfully!")
    return redirect("criteria_list", event_id=event_id)


# Admin: Create Judge Account
@login_required
@user_passes_test(is_admin)
def create_judge(request):
    if request.method == "POST":
        form = JudgeCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            judge_group = Group.objects.get(name="Judge")
            user.groups.add(judge_group)
            return redirect("dashboard")
    else:
        form = JudgeCreationForm()
    return render(request, "home/create_judge.html", {"form": form})


# Judge Dashboard (unchanged for now)
@login_required
@user_passes_test(is_judge)
def judge_dashboard(request):
    events = Event.objects.all()
    candidates = Candidate.objects.all()
    criteria = Criteria.objects.all()
    return render(
        request,
        "home/judge_dashboard.html",
        {"events": events, "candidates": candidates, "criteria": criteria},
    )


@login_required
def score_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    scores = Score.objects.filter(event=event).order_by("judge", "criteria__round")
    preliminary_scores = scores.filter(criteria__round="Preliminary")
    final_scores = scores.filter(criteria__round="Final")
    return render(request, "home/score_list.html", {"event": event, "scores": scores, "rounds": ["Preliminary", "Final"]})



@login_required
def scoring_page(request, event_id):
    if not is_judge(request.user):
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')

    event = get_object_or_404(Event, id=event_id)
    if request.user not in event.judges.all():
        messages.error(request, "You are not a judge for this event.")
        return redirect('judge_dashboard')

    # Get all candidates
    male_candidates = event.candidates.filter(gender="Male").order_by('position')
    female_candidates = event.candidates.filter(gender="Female").order_by('position')
    preliminary_criteria = event.criteria.filter(round="Preliminary")
    final_criteria = event.criteria.filter(round="Final")

    # Calculate top 5 candidates for Final Round based on Preliminary scores
    all_candidates = event.candidates.all()
    prelim_scores = {}
    for candidate in all_candidates:
        total = Score.objects.filter(
            candidate=candidate, 
            event=event, 
            criteria__round="Preliminary"
        ).aggregate(total=Sum('score'))['total'] or 0
        if total > 0:
            prelim_scores[candidate.id] = total
    
    # Get top 5 candidates
    top_candidate_ids = sorted(prelim_scores.items(), key=lambda x: x[1], reverse=True)
    top_candidates = all_candidates.filter(id__in=[cid for cid, _ in top_candidate_ids])
    final_male_candidates = top_candidates.filter(gender="Male").order_by('position')[:5]
    final_female_candidates = top_candidates.filter(gender="Female").order_by('position')[:5]

    # Precompute scores and totals
    prelim_scores_dict = {}
    final_scores_dict = {}
    prelim_total_scores = {}
    final_total_scores = {}
    
    for candidate in all_candidates:
        prelim_scores_dict[candidate.id] = {}
        final_scores_dict[candidate.id] = {}
        
        # Preliminary scores
        prelim_candidate_scores = Score.objects.filter(
            candidate=candidate, 
            judge=request.user, 
            event=event, 
            criteria__round="Preliminary"
        )
        for criterion in preliminary_criteria:
            score = prelim_candidate_scores.filter(criteria=criterion).first()
            prelim_scores_dict[candidate.id][criterion.id] = score.score if score else None
        prelim_total_scores[candidate.id] = prelim_candidate_scores.aggregate(total=Sum('score'))['total'] or 0

        # Final scores (only for top 5)
        if candidate in top_candidates:
            final_candidate_scores = Score.objects.filter(
                candidate=candidate, 
                judge=request.user, 
                event=event, 
                criteria__round="Final"
            )
            for criterion in final_criteria:
                score = final_candidate_scores.filter(criteria=criterion).first()
                final_scores_dict[candidate.id][criterion.id] = score.score if score else None
            final_total_scores[candidate.id] = final_candidate_scores.aggregate(total=Sum('score'))['total'] or 0

    if request.method == "POST" and request.htmx:
        candidate_id = request.POST.get('candidate_id')
        criterion_id = request.POST.get('criterion_id')
        score_value = request.POST.get(f'score_{candidate_id}_{criterion_id}')
        round_type = request.POST.get('round_type')

        if score_value:
            candidate = get_object_or_404(Candidate, id=candidate_id, event=event)
            criteria_set = final_criteria if round_type == "Final" else preliminary_criteria
            criterion = criteria_set.get(id=criterion_id)
            score, created = Score.objects.get_or_create(
                candidate=candidate, 
                criteria=criterion, 
                judge=request.user, 
                event=event,
                defaults={'score': float(score_value)}
            )
            if not created:
                score.score = float(score_value)
                score.save()

            # Calculate the new total score
            total_score = Score.objects.filter(
                candidate=candidate, 
                judge=request.user, 
                event=event,
                criteria__round=round_type
            ).aggregate(total=Sum('score'))['total'] or 0
            
            return HttpResponse(
                f"""
                <td hx-swap-oob="true" id="score-cell-{candidate.id}-{criterion.id}">
                    <span class="text-gray-500">{float(score_value)}</span>
                    <input type="number" 
                           name="score_{candidate.id}_{criterion.id}" 
                           step="1" 
                           min="0" 
                           max="{criterion.percentage}" 
                           class="w-20 p-2 border border-gray-300 rounded-lg hidden" 
                           value="{float(score_value)}"
                           hx-trigger="keyup[keyCode==13]">
                </td>
                <td hx-swap-oob="true" id="total-score-{candidate.id}-{round_type}">
                    <span class="text-gray-500">{total_score}</span>
                </td>
                """
            )

        return HttpResponse(status=204)

    context = {
        'event': event,
        'male_candidates': male_candidates,
        'female_candidates': female_candidates,
        'final_male_candidates': final_male_candidates,
        'final_female_candidates': final_female_candidates,
        'preliminary_criteria': preliminary_criteria,
        'final_criteria': final_criteria,
        'prelim_scores_dict': prelim_scores_dict,
        'final_scores_dict': final_scores_dict,
        'prelim_total_scores': prelim_total_scores,
        'final_total_scores': final_total_scores,
    }
    return render(request, 'home/scoring_page.html', context)


@login_required
def event_scores(request, event_id):
    event = Event.objects.get(id=event_id)
    
    # Get all criteria
    prelim_criteria = Criteria.objects.filter(event=event, round="Preliminary").order_by('title')
    final_criteria = Criteria.objects.filter(event=event, round="Final").order_by('title')
    
    # Get all candidates
    all_candidates = Candidate.objects.filter(event=event)
    
    # Preliminary Round Scores - Average across all judges
    prelim_scores = Score.objects.filter(
        event=event, 
        criteria__round="Preliminary"
    ).values(
        'candidate',
        'candidate__name',
        'candidate__gender',
        'candidate__position',
        'criteria__id',
        'criteria__title'
    ).annotate(avg_score=Avg('score'))
    
    prelim_scores_dict = {}
    prelim_total_scores = {}
    for score in prelim_scores:
        cand_id = score['candidate']
        if cand_id not in prelim_scores_dict:
            prelim_scores_dict[cand_id] = {}
            prelim_total_scores[cand_id] = 0
        prelim_scores_dict[cand_id][score['criteria__id']] = score['avg_score']
        prelim_total_scores[cand_id] += score['avg_score']
    
    # Split candidates by gender and sort with ranks
    female_candidates = all_candidates.filter(gender="Female")
    male_candidates = all_candidates.filter(gender="Male")
    
    sorted_female_candidates = sorted(female_candidates, key=lambda x: prelim_total_scores.get(x.id, 0), reverse=True)
    sorted_male_candidates = sorted(male_candidates, key=lambda x: prelim_total_scores.get(x.id, 0), reverse=True)
    
    # Add ranks to prelim candidates
    prelim_female_ranks = {cand.id: i + 1 for i, cand in enumerate(sorted_female_candidates)}
    prelim_male_ranks = {cand.id: i + 1 for i, cand in enumerate(sorted_male_candidates)}
    
    # Final Round Scores - Top 5 per gender based on prelim avg total
    prelim_female_totals = [(cand_id, total) for cand_id, total in prelim_total_scores.items() 
                           if Candidate.objects.get(id=cand_id).gender == "Female"]
    prelim_male_totals = [(cand_id, total) for cand_id, total in prelim_total_scores.items() 
                         if Candidate.objects.get(id=cand_id).gender == "Male"]
    
    top_5_female = sorted(prelim_female_totals, key=lambda x: x[1], reverse=True)[:5]
    top_5_male = sorted(prelim_male_totals, key=lambda x: x[1], reverse=True)[:5]
    top_5_ids = [cand[0] for cand in top_5_female + top_5_male]
    
    final_scores = Score.objects.filter(
        event=event,
        criteria__round="Final",
        candidate__in=top_5_ids
    ).values(
        'candidate',
        'candidate__name',
        'candidate__gender',
        'candidate__position',
        'criteria__id',
        'criteria__title'
    ).annotate(avg_score=Avg('score'))
    
    final_scores_dict = {}
    final_total_scores = {}
    for score in final_scores:
        cand_id = score['candidate']
        if cand_id not in final_scores_dict:
            final_scores_dict[cand_id] = {}
            final_total_scores[cand_id] = 0
        final_scores_dict[cand_id][score['criteria__id']] = score['avg_score']
        final_total_scores[cand_id] += score['avg_score']
    
    # Split final candidates by gender and sort with ranks
    final_female_candidates = all_candidates.filter(gender="Female", id__in=[cand[0] for cand in top_5_female])
    final_male_candidates = all_candidates.filter(gender="Male", id__in=[cand[0] for cand in top_5_male])
    
    sorted_final_female_candidates = sorted(final_female_candidates, key=lambda x: final_total_scores.get(x.id, 0), reverse=True)
    sorted_final_male_candidates = sorted(final_male_candidates, key=lambda x: final_total_scores.get(x.id, 0), reverse=True)
    
    # Add ranks to final candidates
    final_female_ranks = {cand.id: i + 1 for i, cand in enumerate(sorted_final_female_candidates)}
    final_male_ranks = {cand.id: i + 1 for i, cand in enumerate(sorted_final_male_candidates)}
    
    # Winners - Top 4 per gender from Final Round
    top_4_female_winners = sorted_final_female_candidates[:4]  # Top 4 female winners
    top_4_male_winners = sorted_final_male_candidates[:4]      # Top 4 male winners
    
    # Top 4 overall (for context, though not used in Winners tab anymore)
    final_totals = [(cand_id, total) for cand_id, total in final_total_scores.items()]
    top_4_winners = sorted(final_totals, key=lambda x: x[1], reverse=True)[:4]
    winner_ids = [cand[0] for cand in top_4_winners]
    winner_ranks = {cand_id: i + 1 for i, (cand_id, _) in enumerate(top_4_winners)}
    
    context = {
        'event': event,
        'preliminary_criteria': prelim_criteria,
        'final_criteria': final_criteria,
        'female_candidates': sorted_female_candidates,
        'male_candidates': sorted_male_candidates,
        'final_female_candidates': sorted_final_female_candidates,
        'final_male_candidates': sorted_final_male_candidates,
        'prelim_scores_dict': prelim_scores_dict,
        'prelim_total_scores': prelim_total_scores,
        'final_scores_dict': final_scores_dict,
        'final_total_scores': final_total_scores,
        'prelim_female_ranks': prelim_female_ranks,
        'prelim_male_ranks': prelim_male_ranks,
        'final_female_ranks': final_female_ranks,
        'final_male_ranks': final_male_ranks,
        'winner_ids': winner_ids,
        'winner_ranks': winner_ranks,
        'top_4_female_winners': top_4_female_winners,  # Top 4 female winners
        'top_4_male_winners': top_4_male_winners,      # Top 4 male winners
    }
    
    return render(request, 'home/event_scores.html', context)




