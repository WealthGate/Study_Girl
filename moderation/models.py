from django.contrib.auth.models import User
from django.db import models


class UserReport(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("reviewing", "Reviewing"),
        ("closed", "Closed"),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_made")
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_received", null=True, blank=True)
    reason = models.CharField(max_length=160)
    details = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.reporter.username}: {self.reason}"


class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="notification_preference")
    in_app_distractions_muted = models.BooleanField(default=False)
    email_session_updates = models.BooleanField(default=True)

    def __str__(self):
        return f"Notifications for {self.user.username}"
