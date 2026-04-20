from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from tutoring.models import StudySession


@login_required
def study_room(request, session_id):
    study_session = get_object_or_404(StudySession, pk=session_id)
    if not study_session.user_can_enter(request.user):
        raise PermissionDenied
    if study_session.status == "scheduled":
        study_session.status = "live"
        study_session.started_at = timezone.now()
        study_session.save()
    return render(request, "sessions/study_room.html", {"study_session": study_session})


@login_required
def leave_session(request, session_id):
    study_session = get_object_or_404(StudySession, pk=session_id)
    if not study_session.user_can_enter(request.user):
        raise PermissionDenied
    return redirect("feedback", session_id=study_session.id)
