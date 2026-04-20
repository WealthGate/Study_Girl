from django.contrib import admin
from .models import NotificationPreference, UserReport

admin.site.register(UserReport)
admin.site.register(NotificationPreference)
