from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from profiles.models import TutorApplication, TutorProfile


class StaffDashboardTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user("staff", password="pass12345", is_staff=True)
        self.regular_user = User.objects.create_user("student", password="pass12345")
        self.tutor_user = User.objects.create_user("pendingtutor", password="pass12345")
        self.tutor_profile = TutorProfile.objects.create(
            user=self.tutor_user,
            full_name="Pending Tutor",
            approval_status="pending",
        )
        self.application = TutorApplication.objects.create(user=self.tutor_user)

    def test_staff_dashboard_indicates_who_approves_tutors(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("staff_dashboard"))
        self.assertContains(response, "Staff/admin users approve tutor accounts here")
        self.assertContains(response, "Approve tutor")
        self.assertContains(response, "Make admin")
        self.assertContains(response, "Deactivate")

    def test_staff_can_approve_tutor_application(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("review_tutor_application", args=[self.application.id, "approve"]))
        self.assertRedirects(response, reverse("staff_dashboard"))
        self.application.refresh_from_db()
        self.tutor_profile.refresh_from_db()
        self.assertEqual(self.application.status, "approved")
        self.assertEqual(self.tutor_profile.approval_status, "approved")
        self.assertEqual(self.application.reviewed_by, self.staff)

    def test_staff_can_make_another_user_admin(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("manage_user_access", args=[self.regular_user.id, "make-admin"]))
        self.assertRedirects(response, reverse("staff_dashboard"))
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.is_staff)

    def test_staff_can_deactivate_violator(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("manage_user_access", args=[self.regular_user.id, "deactivate"]))
        self.assertRedirects(response, reverse("staff_dashboard"))
        self.regular_user.refresh_from_db()
        self.assertFalse(self.regular_user.is_active)

    def test_staff_cannot_deactivate_self(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("manage_user_access", args=[self.staff.id, "deactivate"]))
        self.assertRedirects(response, reverse("staff_dashboard"))
        self.staff.refresh_from_db()
        self.assertTrue(self.staff.is_active)
