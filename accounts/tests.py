from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from profiles.models import StudentProfile, TutorApplication, TutorProfile


class SignUpTests(TestCase):
    def test_login_page_links_to_open_signup(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, reverse("signup"))
        self.assertContains(response, "Create your account")

    def test_public_navigation_links_to_admin_login(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, reverse("admin_login"))
        self.assertContains(response, "Admin login")

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


class EnsureAdminCommandTests(TestCase):
    def test_skips_when_admin_credentials_are_missing(self):
        output = StringIO()
        with patch.dict("os.environ", {}, clear=True):
            call_command("ensure_admin", stdout=output)
        self.assertIn("Skipping superadmin setup", output.getvalue())
        self.assertEqual(User.objects.count(), 0)

    def test_creates_superadmin_from_environment(self):
        output = StringIO()
        env = {
            "ADMIN_USERNAME": "admin",
            "ADMIN_PASSWORD": "strong-admin-pass-123",
            "ADMIN_EMAIL": "admin@example.com",
        }
        with patch.dict("os.environ", env, clear=True):
            call_command("ensure_admin", stdout=output)
        user = User.objects.get(username="admin")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("strong-admin-pass-123"))
