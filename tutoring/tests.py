from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from profiles.models import Subject, TutorProfile
from resources.models import SoloStudyResource
from .models import SessionFeedback, SessionRequest, StudySession, StudySisterConnection
from .services import update_connection_after_feedback


class TutoringFlowTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Mathematics")
        self.student = User.objects.create_user("student", password="pass12345")
        self.other = User.objects.create_user("other", password="pass12345")
        self.tutor_user = User.objects.create_user("tutor", password="pass12345")
        self.tutor_profile = TutorProfile.objects.create(user=self.tutor_user, full_name="Tutor", approval_status="approved")
        self.tutor_profile.subjects.add(self.subject)

    def test_only_approved_tutors_show_in_discovery(self):
        pending_user = User.objects.create_user("pending", password="pass12345")
        TutorProfile.objects.create(user=pending_user, full_name="Pending", approval_status="pending")
        self.client.force_login(self.student)
        response = self.client.get(reverse("tutor_list"))
        self.assertContains(response, "Tutor")
        self.assertNotContains(response, "Pending")

    def test_session_request_accept_creates_room(self):
        request = SessionRequest.objects.create(student=self.student, tutor=self.tutor_profile, subject=self.subject)
        session = request.accept()
        self.assertEqual(request.status, "accepted")
        self.assertEqual(session.student, self.student)
        self.assertTrue(session.room_code)

    def test_room_permissions_only_allow_participants(self):
        session = StudySession.objects.create(student=self.student, tutor=self.tutor_user, subject=self.subject)
        self.client.force_login(self.other)
        response = self.client.get(reverse("study_room", args=[session.id]))
        self.assertEqual(response.status_code, 403)

    def test_positive_feedback_activates_study_sisters(self):
        session = StudySession.objects.create(student=self.student, tutor=self.tutor_user, subject=self.subject)
        SessionFeedback.objects.create(session=session, reviewer=self.student, rating=5, was_helpful=True, wants_to_continue=True)
        SessionFeedback.objects.create(session=session, reviewer=self.tutor_user, rating=5, was_helpful=True, wants_to_continue=True)
        connection = update_connection_after_feedback(session)
        self.assertEqual(connection.status, "active")
        self.assertEqual(connection.session_count, 1)

    def test_vibe_unlocks_after_five_sessions(self):
        connection = StudySisterConnection.objects.create(student=self.student, tutor=self.tutor_user, status="active", session_count=4)
        connection.add_completed_session()
        self.assertTrue(connection.vibe_unlocked)

    def test_resource_library_view(self):
        SoloStudyResource.objects.create(title="Math notes", subject=self.subject, is_approved=True)
        self.client.force_login(self.student)
        response = self.client.get(reverse("resource_library"))
        self.assertContains(response, "Math notes")

    def test_feedback_submission(self):
        session = StudySession.objects.create(student=self.student, tutor=self.tutor_user, subject=self.subject)
        self.client.force_login(self.student)
        response = self.client.post(reverse("feedback", args=[session.id]), {
            "rating": 5,
            "was_helpful": "on",
            "wants_to_continue": "on",
            "comment": "Very helpful",
        })
        self.assertRedirects(response, reverse("study_sisters"))
        self.assertTrue(SessionFeedback.objects.filter(session=session, reviewer=self.student).exists())
