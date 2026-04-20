from django import forms
from .models import StudentProfile, TutorApplication, TutorProfile


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            "full_name",
            "school",
            "form_year",
            "subjects_needing_help",
            "learning_style",
            "short_intro",
            "avatar",
            "location",
            "favorite_study_times",
            "preferred_traits",
        ]
        widgets = {
            "subjects_needing_help": forms.CheckboxSelectMultiple,
            "preferred_traits": forms.CheckboxSelectMultiple,
        }


class TutorProfileForm(forms.ModelForm):
    class Meta:
        model = TutorProfile
        fields = [
            "full_name",
            "school",
            "form_year",
            "subjects",
            "short_bio",
            "personality_traits",
            "profile_picture",
            "tutoring_style",
            "availability",
        ]
        widgets = {
            "subjects": forms.CheckboxSelectMultiple,
            "personality_traits": forms.CheckboxSelectMultiple,
        }


class TutorApplicationForm(forms.ModelForm):
    class Meta:
        model = TutorApplication
        fields = [
            "why_tutor",
            "agrees_to_guidelines",
            "checklist_subject_confidence",
            "checklist_kind_communication",
            "checklist_safe_online_behavior",
        ]
