from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from seller.models import Seller

@receiver(user_signed_up)
def create_seller_for_social_account(request, user, **kwargs):
    # READ ROLE SAFELY FROM GET PARAM
    role = request.GET.get("role", "customer")

    # Assign user role
    user.role = role
    user.save()

    # If seller, create seller profile
    if role == "seller":
        Seller.objects.get_or_create(
            user=user,
            defaults={"shop_name": f"{user.username}'s Shop"}
        )
