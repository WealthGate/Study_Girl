from django import forms
from .models import SoloStudyResource


class SoloStudyResourceForm(forms.ModelForm):
    class Meta:
        model = SoloStudyResource
        fields = ["title", "subject", "resource_type", "description", "file", "external_link", "thumbnail"]
