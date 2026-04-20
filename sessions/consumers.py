import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import ChatMessage, WhiteboardEvent
from tutoring.models import StudySession


class StudyRoomConsumer(AsyncWebsocketConsumer):
    """One WebSocket handles signaling, chat, presence, and whiteboard events.

    WebRTC sends audio/video directly between browsers. Django Channels is only
    the meeting helper: it passes offers, answers, ICE candidates, chat, and
    drawing messages to the other participant.
    """

    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        self.room_group_name = f"study_room_{self.session_id}"
        self.user = self.scope["user"]

        allowed = await self.user_allowed()
        if not allowed:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "room_event", "payload": {"type": "presence", "user": self.user.username, "status": "joined"}},
        )

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "room_event", "payload": {"type": "presence", "user": self.user.username, "status": "left"}},
            )
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        payload = json.loads(text_data)
        event_type = payload.get("type")

        if event_type == "chat":
            await self.save_chat(payload.get("message", ""))
        elif event_type in ["draw", "clear_board"]:
            await self.save_whiteboard(event_type, payload)

        payload["user"] = self.user.username
        await self.channel_layer.group_send(self.room_group_name, {"type": "room_event", "payload": payload})

    async def room_event(self, event):
        await self.send(text_data=json.dumps(event["payload"]))

    @sync_to_async
    def user_allowed(self):
        if not self.user.is_authenticated:
            return False
        try:
            session = StudySession.objects.get(pk=self.session_id)
        except StudySession.DoesNotExist:
            return False
        return session.user_can_enter(self.user)

    @sync_to_async
    def save_chat(self, message):
        if message.strip():
            ChatMessage.objects.create(session_id=self.session_id, sender=self.user, message=message[:1000])

    @sync_to_async
    def save_whiteboard(self, event_type, payload):
        WhiteboardEvent.objects.create(session_id=self.session_id, sender=self.user, event_type=event_type, payload=payload)
