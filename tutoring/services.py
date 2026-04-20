from django.db.models import Avg

from profiles.models import TutorProfile
from .models import SessionFeedback, StudySisterConnection


def update_connection_after_feedback(session):
    """Apply the simple Study Sisters business rules after feedback is submitted."""
    feedback = list(session.feedback.all())
    if len(feedback) < 2:
        return None

    connection, _ = StudySisterConnection.objects.get_or_create(
        student=session.student,
        tutor=session.tutor,
    )

    if all(item.is_positive for item in feedback):
        connection.status = "active"
        if session.status != "completed":
            session.mark_completed()
        connection.add_completed_session()
    else:
        connection.status = "pending"
        connection.save()

    tutor_profile = TutorProfile.objects.filter(user=session.tutor).first()
    if tutor_profile:
        tutor_profile.completed_sessions = session.tutor.tutor_study_sessions.filter(status="completed").count()
        tutor_profile.average_rating = SessionFeedback.objects.filter(session__tutor=session.tutor).aggregate(Avg("rating"))["rating__avg"] or 0
        tutor_profile.vibes_earned = StudySisterConnection.objects.filter(tutor=session.tutor, vibe_unlocked=True).count()
        tutor_profile.save()

    return connection
