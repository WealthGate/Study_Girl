from django.contrib.auth.models import User
from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class PersonalityTrait(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    full_name = models.CharField(max_length=120)
    school = models.CharField(max_length=120, default="Wesley High School")
    form_year = models.CharField(max_length=50, blank=True)
    subjects_needing_help = models.ManyToManyField(Subject, blank=True, related_name="students_needing_help")
    learning_style = models.CharField(max_length=120, blank=True)
    short_intro = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    location = models.CharField(max_length=120, default="Dominica")
    favorite_study_times = models.CharField(max_length=160, blank=True)
    preferred_traits = models.ManyToManyField(PersonalityTrait, blank=True)

    def __str__(self):
        return self.full_name


class TutorProfile(models.Model):
    APPROVAL_CHOICES = [
        ("pending", "Pending approval"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="tutor_profile")
    full_name = models.CharField(max_length=120)
    school = models.CharField(max_length=120, default="Wesley High School")
    form_year = models.CharField(max_length=50, blank=True)
    subjects = models.ManyToManyField(Subject, blank=True, related_name="tutors")
    short_bio = models.TextField(blank=True)
    personality_traits = models.ManyToManyField(PersonalityTrait, blank=True)
    profile_picture = models.ImageField(upload_to="tutors/", blank=True, null=True)
    tutoring_style = models.CharField(max_length=160, blank=True)
    availability = models.CharField(max_length=180, blank=True)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default="pending")
    completed_sessions = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    vibes_earned = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-average_rating", "-completed_sessions", "full_name"]

    @property
    def is_approved(self):
        return self.approval_status == "approved"

    def __str__(self):
        return self.full_name


class TutorApplication(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="tutor_application")
    why_tutor = models.TextField(blank=True)
    agrees_to_guidelines = models.BooleanField(default=False)
    checklist_subject_confidence = models.BooleanField(default=False)
    checklist_kind_communication = models.BooleanField(default=False)
    checklist_safe_online_behavior = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_tutor_applications")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def ready_for_review(self):
        return (
            self.agrees_to_guidelines
            and self.checklist_subject_confidence
            and self.checklist_kind_communication
            and self.checklist_safe_online_behavior
        )

    def __str__(self):
        return f"Tutor application for {self.user.username}"
