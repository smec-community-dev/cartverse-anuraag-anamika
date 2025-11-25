import json
from channels.generic.websocket import AsyncWebsocketConsumer

class UserNotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
            return

        # MUST match utils.py
        self.group_name = f"user_{user.id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # MUST match "type": "send_notification"
    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "title": event.get("title"),
            "message": event.get("message"),
            "product_name": event.get("product_name"),
            "price": event.get("price"),
            "link": event.get("link")
        }))
