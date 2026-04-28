from django.test import TestCase
from django.urls import reverse

from profiles.models import StudentProfile, TutorApplication, TutorProfile


class SignUpTests(TestCase):
    def test_login_page_links_to_open_signup(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, reverse("signup"))
        self.assertContains(response, "Create your account")

    def test_signup_page_links_back_to_login(self):
        response = self.client.get(reverse("signup"))
        self.assertContains(response, "Students can create their own username and password")
        self.assertContains(response, reverse("login"))

    def test_student_signup_creates_profile_and_logs_in(self):
        response = self.client.post(reverse("signup"), {
            "username": "amara",
            "email": "amara@example.com",
            "password1": "strong-pass-123",
            "password2": "strong-pass-123",
            "role": "student",
        })
        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(StudentProfile.objects.filter(user__username="amara").exists())

    def test_tutor_signup_creates_pending_profile_and_application(self):
        self.client.post(reverse("signup"), {
            "username": "tutoramara",
            "email": "tutoramara@example.com",
            "password1": "strong-pass-123",
            "password2": "strong-pass-123",
            "role": "tutor",
        })
        self.assertTrue(TutorProfile.objects.filter(user__username="tutoramara", approval_status="pending").exists())
        self.assertTrue(TutorApplication.objects.filter(user__username="tutoramara").exists())
