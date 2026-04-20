from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import StudentProfileForm, TutorApplicationForm, TutorProfileForm
from .models import StudentProfile, TutorApplication, TutorProfile


@login_required
def edit_student_profile(request):
    profile, _ = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={"full_name": request.user.username, "school": "Wesley High School"},
    )
    form = StudentProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student profile saved.")
        return redirect("dashboard")
    return render(request, "profiles/student_profile_form.html", {"form": form})


@login_required
def edit_tutor_profile(request):
    profile, _ = TutorProfile.objects.get_or_create(
        user=request.user,
        defaults={"full_name": request.user.username, "school": "Wesley High School"},
    )
    application, _ = TutorApplication.objects.get_or_create(user=request.user)
    profile_form = TutorProfileForm(request.POST or None, request.FILES or None, instance=profile)
    application_form = TutorApplicationForm(request.POST or None, instance=application)
    if request.method == "POST" and profile_form.is_valid() and application_form.is_valid():
        profile_form.save()
        application_form.save()
        messages.success(request, "Tutor application saved. An admin must approve it before students can find you.")
        return redirect("dashboard")
    return render(
        request,
        "profiles/tutor_profile_form.html",
        {"profile_form": profile_form, "application_form": application_form, "application": application},
    )


@login_required
def tutor_profile_detail(request, pk):
    tutor = get_object_or_404(TutorProfile, pk=pk, approval_status="approved")
    return render(request, "profiles/tutor_profile_detail.html", {"tutor": tutor})
