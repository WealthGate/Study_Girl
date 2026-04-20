from django.contrib import admin
from .models import PersonalityTrait, StudentProfile, Subject, TutorApplication, TutorProfile

admin.site.register(Subject)
admin.site.register(PersonalityTrait)
admin.site.register(StudentProfile)
admin.site.register(TutorProfile)
admin.site.register(TutorApplication)
