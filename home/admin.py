from django.contrib import admin
from .models import Candidate, Criteria, Event, Score

admin.site.register(Candidate)
admin.site.register(Criteria)
admin.site.register(Event)
admin.site.register(Score)