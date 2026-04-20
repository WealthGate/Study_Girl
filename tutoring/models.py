from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from profiles.models import Subject, TutorProfile


class SessionRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
        ("cancelled", "Cancelled"),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_session_requests")
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name="session_requests")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    message = models.TextField(blank=True)
    requested_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def accept(self):
        self.status = "accepted"
        self.save()
        return StudySession.objects.create(
            session_request=self,
            student=self.student,
            tutor=self.tutor.user,
            subject=self.subject,
            status="scheduled",
        )

    def decline(self):
        self.status = "declined"
        self.save()

    def __str__(self):
        return f"{self.student.username} asks {self.tutor.full_name} for {self.subject}"


class StudySession(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("live", "Live"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    session_request = models.OneToOneField(SessionRequest, on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_study_sessions")
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tutor_study_sessions")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    room_code = models.CharField(max_length=40, unique=True, blank=True)
    focus_warnings = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.room_code:
            self.room_code = f"room-{timezone.now().strftime('%Y%m%d%H%M%S%f')}"
        super().save(*args, **kwargs)

    def user_can_enter(self, user):
        return user.is_staff or user == self.student or user == self.tutor

    def mark_completed(self):
        self.status = "completed"
        self.ended_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.student.username} and {self.tutor.username} - {self.subject}"


class SessionFeedback(models.Model):
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE, related_name="feedback")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=5)
    was_helpful = models.BooleanField(default=True)
    wants_to_continue = models.BooleanField(default=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["session", "reviewer"]

    @property
    def is_positive(self):
        return self.was_helpful and self.wants_to_continue and self.rating >= 4

    def __str__(self):
        return f"{self.reviewer.username} feedback for session {self.session_id}"


class StudySisterConnection(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("active", "Active"),
        ("ended", "Ended"),
        ("blocked", "Blocked"),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_sister_connections")
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tutor_sister_connections")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    session_count = models.PositiveIntegerField(default=0)
    vibe_unlocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["student", "tutor"]

    def add_completed_session(self):
        self.session_count += 1
        if self.session_count >= 5:
            self.vibe_unlocked = True
            VibeAward.objects.get_or_create(connection=self, name="SBS Vibe")
        self.save()

    def __str__(self):
        return f"{self.student.username} + {self.tutor.username}"


class VibeAward(models.Model):
    connection = models.ForeignKey(StudySisterConnection, on_delete=models.CASCADE, related_name="vibe_awards")
    name = models.CharField(max_length=80, default="SBS Vibe")
    awarded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
