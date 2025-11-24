from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.account.signals import user_signed_up
from .models import Customer

User = get_user_model()


# 1️⃣ When a user signs up via Google or AllAuth, set role & create profile
@receiver(user_signed_up)
def on_google_signup(request, user, **kwargs):
    # ensure role is customer
    if not user.role:
        user.role = "customer"
        user.save(update_fields=["role"])

    # ensure customer profile exists
    Customer.objects.get_or_create(user=user)


# 2️⃣ When user created manually or via registration
@receiver(post_save, sender=User)
def on_user_create(sender, instance, created, **kwargs):
    if created:
        Customer.objects.get_or_create(user=instance)

        if not instance.role:
            instance.role = "customer"
            instance.save(update_fields=["role"])
