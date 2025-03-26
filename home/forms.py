from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Candidate, Criteria, Event

class JudgeCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text="Enter the judge's full name.")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter a unique username'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter the judge\'s full name'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Enter a strong password'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Re-enter your password'}),
            
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        if commit:
            user.save()
        return user


    

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'venue', 'start_date', 'end_date', 'description', 'judges']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={
                'placeholder': 'Provide a brief description of the event'
            }),
            'judges': forms.SelectMultiple(attrs={
                'placeholder': 'Select judges'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter event title'
            }),
            'venue': forms.TextInput(attrs={
                'placeholder': 'Enter venue'
            }),
        }
        

class JudgeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'password']
        widgets = {'password': forms.PasswordInput}     

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'gender', 'picture', 'position']

class CriteriaForm(forms.ModelForm):
    class Meta:
        model = Criteria
        fields = ['round', 'title', 'percentage']