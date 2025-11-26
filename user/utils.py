from .models import UserNotification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_user_notification(user, title, message, product_name=None, price=None, link=None):
    # Save Notification to DB
    UserNotification.objects.create(
        user=user,
        title=title,
        message=message,
        product_name=product_name,
        price=price
    )

    # Websocket Broadcast
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "send_notification",
            "title": title,
            "message": message,
            "product_name": product_name,
            "price": price,
            "link": link
        }
    )
