from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from seller.models import Seller

@receiver(user_signed_up)
def create_seller_for_social_account(request, user, **kwargs):
    # if request.session  and request.session['role']:
    #     user.role = request.session['role']
    # else:
    #     user.role = "user"
    role = request.GET.get("role", "customer")
    user.role=role

    # Mark role as seller

    user.save()

    # Create linked seller profile
    if not Seller.objects.filter(user=user).exists() :
        Seller.objects.create(
            user=user,
            shop_name=f"{user.username}'s Shop"
        )
