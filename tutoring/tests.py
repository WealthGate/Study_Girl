from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from profiles.models import Subject, TutorProfile
from resources.models import SoloStudyResource
from .models import SessionFeedback, SessionRequest, StudySession, StudySessionParticipant, StudySisterConnection
from .services import update_connection_after_feedback


class TutoringFlowTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Mathematics")
        self.student = User.objects.create_user("student", password="pass12345")
        self.other = User.objects.create_user("other", password="pass12345")
        self.second_student = User.objects.create_user("secondstudent", password="pass12345")
        self.tutor_user = User.objects.create_user("tutor", password="pass12345")
        self.second_tutor_user = User.objects.create_user("teacher", password="pass12345")
        self.tutor_profile = TutorProfile.objects.create(user=self.tutor_user, full_name="Tutor", approval_status="approved")
        self.second_tutor_profile = TutorProfile.objects.create(user=self.second_tutor_user, full_name="Teacher", approval_status="approved")
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
        self.assertTrue(session.participants.filter(user=self.student, role="student", status="approved").exists())
        self.assertTrue(session.participants.filter(user=self.tutor_user, role="lead_tutor", status="approved").exists())

    def test_accepted_students_for_same_tutor_subject_share_class_room(self):
        first_request = SessionRequest.objects.create(student=self.student, tutor=self.tutor_profile, subject=self.subject)
        second_request = SessionRequest.objects.create(student=self.second_student, tutor=self.tutor_profile, subject=self.subject)
        first_session = first_request.accept()
        second_session = second_request.accept()
        self.assertEqual(first_session, second_session)
        self.assertTrue(first_session.user_can_enter(self.student))
        self.assertTrue(first_session.user_can_enter(self.second_student))

    def test_room_permissions_only_allow_participants(self):
        session = StudySession.objects.create(student=self.student, tutor=self.tutor_user, subject=self.subject)
        self.client.force_login(self.other)
        response = self.client.get(reverse("study_room", args=[session.id]))
        self.assertEqual(response.status_code, 403)

    def test_approved_teacher_can_join_with_teacher_link(self):
        session = StudySession.objects.create(student=self.student, tutor=self.tutor_user, subject=self.subject)
        self.client.force_login(self.second_tutor_user)
        response = self.client.get(reverse("join_teacher_class", args=[session.id, session.room_code]))
        self.assertRedirects(response, reverse("study_room", args=[session.id]))
        self.assertTrue(StudySessionParticipant.objects.filter(session=session, user=self.second_tutor_user, role="teacher").exists())

    def test_student_cannot_join_with_teacher_link(self):
        session = StudySession.objects.create(student=self.student, tutor=self.tutor_user, subject=self.subject)
        self.client.force_login(self.other)
        response = self.client.get(reverse("join_teacher_class", args=[session.id, session.room_code]))
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
