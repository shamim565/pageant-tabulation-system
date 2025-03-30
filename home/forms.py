from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Candidate, Criteria, Event
from django.db import IntegrityError

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

class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': "Incorrect username or password. Please try again.",
    }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'venue', 'start_date', 'end_date', 'description', 'judges']
        labels = {
            'venue': 'Location', 
        }
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
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label="New Password",
        help_text="Leave blank to keep the current password."
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label="Confirm New Password",
        help_text="Re-enter the new password to confirm."
    )

    class Meta:
        model = User
        fields = ['username', 'first_name'] 
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter a unique username'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter judge\'s full name'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        # Validate password mismatch
        if password and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match.")

        # Validate username uniqueness (in case the instance is being edited)
        username = cleaned_data.get("username")
        if username:
            # Exclude the current user from the uniqueness check
            existing_user = User.objects.filter(username=username).exclude(pk=self.instance.pk if self.instance else None)
            if existing_user.exists():
                self.add_error('username', "A user with this username already exists.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            try:
                user.save()
            except IntegrityError as e:
                raise forms.ValidationError(f"Error saving user: {str(e)}")
        return user

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'gender', 'position', 'picture']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter candidate name'}),
            'gender': forms.Select(choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")]),
            'position': forms.NumberInput(attrs={'placeholder': 'Enter position (e.g., 1)'}),
            'picture': forms.FileInput(),
        }

class CriteriaForm(forms.ModelForm):
    class Meta:
        model = Criteria
        fields = ['round', 'title', 'percentage']
        widgets = {
            'round': forms.Select(choices=[("Preliminary", "Preliminary"), ("Final", "Final")]),
            'title': forms.TextInput(attrs={'placeholder': 'Enter criteria title'}),
            'percentage': forms.NumberInput(attrs={'placeholder': 'Enter percentage (e.g., 30)', 'step': '0.1'}),
        }