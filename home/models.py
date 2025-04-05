from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Event(models.Model):
    title = models.CharField(max_length=100)
    venue = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="events"
    )
    judges = models.ManyToManyField(User, related_name="judged_events")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_active(self):
        return self.start_date <= date.today() <= self.end_date

    def __str__(self):
        return self.title

class Criteria(models.Model):
    ROUND_CHOICES = [("Preliminary", "Preliminary"), ("Final", "Final")]
    round = models.CharField(max_length=20, choices=ROUND_CHOICES)
    title = models.CharField(max_length=100)
    percentage = models.FloatField(help_text="Percentage weight (e.g., 30 for 30%)")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="criteria"
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="criteria")  # Added
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.round})"

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(
        max_length=10,
        choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")],
    )
    picture = models.ImageField(upload_to="candidate_pics/", default="candidate_pics/default")
    position = models.PositiveIntegerField()
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="candidates"
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="candidates")  # Added
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Score(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    criteria = models.ForeignKey(Criteria, on_delete=models.CASCADE)
    judge = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scores")
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.candidate} - {self.criteria}: {self.score}"