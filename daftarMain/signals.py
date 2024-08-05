from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import OfficeUser, OfficeManager

@receiver(post_save, sender=OfficeUser)
@receiver(post_save, sender=OfficeManager)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a new User
        user = User.objects.create_user(
            username=instance.phone,
            password=instance.code_meli,
        )
        instance.user = user
        instance.save()
    else:
        # Update the existing User
        user = instance.user
        user.username = instance.phone
        if instance.code_meli:  # Only update the password if it's set
            user.set_password(instance.code_meli)
        user.save()
