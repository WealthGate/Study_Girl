from django import forms
from .models import SessionFeedback, SessionRequest


class SessionRequestForm(forms.ModelForm):
    class Meta:
        model = SessionRequest
        fields = ["subject", "message", "requested_time"]
        widgets = {
            "requested_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class SessionFeedbackForm(forms.ModelForm):
    class Meta:
        model = SessionFeedback
        fields = ["rating", "was_helpful", "wants_to_continue", "comment"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
        }
