from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("tutor", "Tutor applicant"),
    ]

    email = forms.EmailField()
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "role"]
