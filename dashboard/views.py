from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Avg
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from moderation.models import UserReport
from profiles.models import StudentProfile, TutorApplication, TutorProfile
from resources.models import SoloStudyResource
from tutoring.models import SessionFeedback, SessionRequest, StudySession, StudySisterConnection


def home(request):
    return render(request, "dashboard/home.html")


def about(request):
    return render(request, "dashboard/about.html")


@login_required
def dashboard(request):
    student_profile = getattr(request.user, "student_profile", None)
    tutor_profile = getattr(request.user, "tutor_profile", None)
    my_sessions = StudySession.objects.filter(student=request.user) | StudySession.objects.filter(tutor=request.user)
    requests = SessionRequest.objects.filter(student=request.user)
    if tutor_profile:
        requests = requests | SessionRequest.objects.filter(tutor=tutor_profile)
    return render(
        request,
        "dashboard/dashboard.html",
        {
            "student_profile": student_profile,
            "tutor_profile": tutor_profile,
            "my_sessions": my_sessions.distinct().order_by("-created_at")[:6],
            "requests": requests.distinct().order_by("-created_at")[:6],
        },
    )


@user_passes_test(lambda user: user.is_staff)
def staff_dashboard(request):
    feedback_average = SessionFeedback.objects.aggregate(Avg("rating"))["rating__avg"] or 0
    context = {
        "total_users": User.objects.count(),
        "total_students": StudentProfile.objects.count(),
        "total_tutors": TutorProfile.objects.filter(approval_status="approved").count(),
        "pending_tutors": TutorApplication.objects.filter(status="pending").count(),
        "total_sessions": StudySession.objects.count(),
        "active_connections": StudySisterConnection.objects.filter(status="active").count(),
        "feedback_average": round(feedback_average, 2),
        "open_reports": UserReport.objects.filter(status="open").count(),
        "resources": SoloStudyResource.objects.count(),
        "pending_applications": TutorApplication.objects.filter(status="pending").select_related("user")[:8],
    }
    return render(request, "dashboard/staff_dashboard.html", context)


@user_passes_test(lambda user: user.is_staff)
def review_tutor_application(request, application_id, action):
    application = get_object_or_404(TutorApplication, pk=application_id)
    tutor_profile = getattr(application.user, "tutor_profile", None)
    if action == "approve":
        application.status = "approved"
        if tutor_profile:
            tutor_profile.approval_status = "approved"
            tutor_profile.save()
        messages.success(request, f"{application.user.username} approved as a tutor.")
    else:
        application.status = "rejected"
        if tutor_profile:
            tutor_profile.approval_status = "rejected"
            tutor_profile.save()
        messages.warning(request, f"{application.user.username} tutor application rejected.")
    application.reviewed_by = request.user
    application.reviewed_at = timezone.now()
    application.save()
    return redirect("staff_dashboard")
