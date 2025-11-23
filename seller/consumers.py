import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
            return

        self.group_name = f"user_{user.id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "notify",
                "message": message,
            }
        )

    async def notify(self, event):
        await self.send(text_data=json.dumps({
            "title": event.get("title", "New Notification"),
            "message": event["message"]
        }))

