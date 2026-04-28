from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from profiles.models import StudentProfile, TutorApplication, TutorProfile
from .forms import SignUpForm


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.save()

            role = form.cleaned_data["role"]
            if role == "student":
                StudentProfile.objects.create(user=user, full_name=user.username, school="Wesley High School")
            else:
                TutorProfile.objects.create(user=user, full_name=user.username, school="Wesley High School")
                TutorApplication.objects.create(user=user)

            login(request, user)
            messages.success(request, "Welcome to Study Girl. Please complete your profile.")
            return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})
