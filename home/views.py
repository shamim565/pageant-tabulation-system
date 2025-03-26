from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import Candidate, Criteria, Event, Score
from django.contrib.auth.models import User, Group
from .forms import JudgeCreationForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .forms import EventForm, JudgeForm, CriteriaForm
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
        candidates = Candidate.objects.filter(created_by=request.user)
        criteria = Criteria.objects.filter(created_by=request.user)
        events = Event.objects.filter(created_by=request.user)
        return render(
            request,
            "home/admin_dashboard.html",
            {"candidates": candidates, "criteria": criteria, "events": events},
        )
    elif is_judge(request.user):
        return render(request, "home/judge_dashboard.html")
    return redirect("login")


# Event Views
# @login_required
# @user_passes_test(is_admin, login_url="dashboard")
# def event_create(request):
#     if request.method == "POST":
#         form = EventForm(request.POST)
#         if form.is_valid():
#             event = form.save(commit=False)
#             event.created_by = request.user
#             event.save()
#             form.save_m2m()  # Save the many-to-many judges field
#             messages.success(request, f'Event "{event.title}" created successfully!')
#             return redirect("event_list")
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = EventForm()
#     judges = User.objects.filter(is_superuser=False)
#     return render(request, "home/event_create.html", {"form": form, "judges": judges})


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
            # messages.success(request, f"Event '{event.title}' created successfully!")
            return redirect("event_list")  # Replace with your success URL
    else:
        form = EventForm()

    # Fetch all judges from the database
    judges = User.objects.filter(is_superuser=False)

    return render(
        request,
        "home/event_create.html",
        {
            "form": form,
            "judges": judges,
        },
    )


@login_required
def event_list(request):
    query = request.GET.get("q", "")
    events = Event.objects.filter(
        Q(title__icontains=query) | Q(venue__icontains=query)
    ).order_by("-created_at")
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
            return redirect("event_list")  # Replace with your success URL

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
    messages.success(request, "Event deleted successfully!")
    return redirect("event_list")


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, "home/event_detail.html", {"event": event})


# Judge Views
@login_required
def judge_list(request):
    query = request.GET.get("q", "")
    judges = User.objects.filter(Q(username__icontains=query)&Q(is_superuser=False)).order_by("username")
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


# @login_required
# def judge_create(request):
#     if request.method == "POST":
#         form = JudgeCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data["password"])
#             user.save()
#             return redirect("judge_list")
#     else:
#         form = JudgeCreationForm()
#     return render(request, "home/judge_create.html", {"form": form})

@login_required
def judge_create(request):
    if request.method == "POST":
        form = JudgeCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Simplified, no need for set_password
            # messages.success(request, "Judge created successfully!")
            return redirect("judge_list")
    else:
        form = JudgeCreationForm()
    return render(request, "home/judge_create.html", {"form": form})


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
    return render(request, "scores/score_list.html", {"event": event, "scores": scores})


@login_required
@user_passes_test(is_judge)
def submit_score(request):
    if request.method == "POST":
        candidate_id = request.POST["candidate"]
        criteria_id = request.POST["criteria"]
        pageant_id = request.POST["pageant"]
        score_value = request.POST["score"]
        Score.objects.create(
            candidate_id=candidate_id,
            criteria_id=criteria_id,
            pageant_id=pageant_id,
            judge=request.user,
            score=score_value,
        )
        return redirect("judge_dashboard")
    return render(request, "home/judge_dashboard.html")
