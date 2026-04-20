from django.contrib.auth.models import User
from django.db import models

from tutoring.models import StudySession


class ChatMessage(models.Model):
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE, related_name="chat_messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender.username}: {self.message[:30]}"


class WhiteboardEvent(models.Model):
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE, related_name="whiteboard_events")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=30)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} in session {self.session_id}"
