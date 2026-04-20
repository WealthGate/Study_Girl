from django.contrib import admin
from .models import SessionFeedback, SessionRequest, StudySession, StudySisterConnection, VibeAward

admin.site.register(SessionRequest)
admin.site.register(StudySession)
admin.site.register(SessionFeedback)
admin.site.register(StudySisterConnection)
admin.site.register(VibeAward)
