from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from seller.models import Seller

@receiver(user_signed_up)
def create_seller_for_social_account(request, user, **kwargs):
    # Mark role as seller
    user.role = "seller"
    user.save()

    # Create linked seller profile
    if not Seller.objects.filter(user=user).exists():
        Seller.objects.create(
            user=user,
            shop_name=f"{user.username}'s Shop"
        )
