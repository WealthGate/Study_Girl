from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from profiles.models import PersonalityTrait, Subject, TutorProfile
from .forms import SessionFeedbackForm, SessionRequestForm
from .models import SessionRequest, StudySession, StudySisterConnection
from .services import update_connection_after_feedback


@login_required
def tutor_list(request):
    tutors = TutorProfile.objects.filter(approval_status="approved").prefetch_related("subjects", "personality_traits")
    subjects = Subject.objects.all()
    traits = PersonalityTrait.objects.all()

    subject = request.GET.get("subject")
    trait = request.GET.get("trait")
    availability = request.GET.get("availability")
    school = request.GET.get("school")
    sort = request.GET.get("sort", "rating")

    if subject:
        tutors = tutors.filter(subjects_id=subject)
    if trait:
        tutors = tutors.filter(personality_traits_id=trait)
    if availability:
        tutors = tutors.filter(availability__icontains=availability)
    if school:
        tutors = tutors.filter(school__icontains=school)
    if sort == "sessions":
        tutors = tutors.order_by("-completed_sessions")

    return render(request, "tutoring/tutor_list.html", {"tutors": tutors, "subjects": subjects, "traits": traits})


@login_required
def request_session(request, tutor_id):
    tutor = get_object_or_404(TutorProfile, pk=tutor_id, approval_status="approved")
    form = SessionRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        session_request = form.save(commit=False)
        session_request.student = request.user
        session_request.tutor = tutor
        session_request.save()
        messages.success(request, "Session request sent.")
        return redirect("session_requests")
    return render(request, "tutoring/request_session.html", {"form": form, "tutor": tutor})


@login_required
def session_requests(request):
    sent = SessionRequest.objects.filter(student=request.user).select_related("tutor", "subject")
    received = SessionRequest.objects.none()
    if hasattr(request.user, "tutor_profile"):
        received = SessionRequest.objects.filter(tutor=request.user.tutor_profile).select_related("student", "subject")
    return render(request, "tutoring/session_requests.html", {"sent": sent, "received": received})


@login_required
def respond_to_request(request, request_id, action):
    session_request = get_object_or_404(SessionRequest, pk=request_id)
    if not hasattr(request.user, "tutor_profile") or session_request.tutor != request.user.tutor_profile:
        raise PermissionDenied
    if action == "accept":
        study_session = session_request.accept()
        messages.success(request, "Request accepted and study room created.")
        return redirect("study_room", session_id=study_session.id)
    session_request.decline()
    messages.info(request, "Request declined.")
    return redirect("session_requests")


@login_required
def feedback(request, session_id):
    study_session = get_object_or_404(StudySession, pk=session_id)
    if not study_session.user_can_enter(request.user):
        raise PermissionDenied
    existing = study_session.feedback.filter(reviewer=request.user).first()
    form = SessionFeedbackForm(request.POST or None, instance=existing)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.session = study_session
        item.reviewer = request.user
        item.save()
        connection = update_connection_after_feedback(study_session)
        if connection and connection.vibe_unlocked:
            messages.success(request, "Feedback saved. SBS Vibe badge unlocked.")
        else:
            messages.success(request, "Feedback saved.")
        return redirect("study_sisters")
    return render(request, "tutoring/feedback.html", {"form": form, "study_session": study_session})


@login_required
def study_sisters(request):
    connections = StudySisterConnection.objects.filter(student=request.user) | StudySisterConnection.objects.filter(tutor=request.user)
    return render(request, "tutoring/study_sisters.html", {"connections": connections.distinct()})


@login_required
def block_connection(request, connection_id):
    connection = get_object_or_404(StudySisterConnection, pk=connection_id)
    if request.user not in [connection.student, connection.tutor]:
        raise PermissionDenied
    connection.status = "blocked"
    connection.save()
    messages.warning(request, "Connection blocked. A staff member can review reports if needed.")
    return redirect("study_sisters")
