from django.contrib.auth.models import User
from django.db import models

from profiles.models import Subject


class SoloStudyResource(models.Model):
    RESOURCE_TYPES = [
        ("note", "Notes/PDF"),
        ("video", "Video link"),
        ("playlist", "Study playlist"),
        ("ambience", "Focus ambience"),
    ]

    title = models.CharField(max_length=160)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default="note")
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="resources/", blank=True, null=True)
    external_link = models.URLField(blank=True)
    thumbnail = models.ImageField(upload_to="resource_thumbnails/", blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["subject__name", "title"]

    def __str__(self):
        return self.title
