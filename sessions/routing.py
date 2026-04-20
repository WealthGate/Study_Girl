from django.urls import path
from .consumers import StudyRoomConsumer

websocket_urlpatterns = [
    path("ws/study-room/<int:session_id>/", StudyRoomConsumer.as_asgi()),
]
