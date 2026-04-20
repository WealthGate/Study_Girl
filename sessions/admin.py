from django.contrib import admin
from .models import ChatMessage, WhiteboardEvent

admin.site.register(ChatMessage)
admin.site.register(WhiteboardEvent)
