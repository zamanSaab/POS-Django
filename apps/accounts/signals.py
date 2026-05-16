from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, NotificationPreferences


@receiver(post_save, sender=User)
def create_notification_prefs(sender, instance, created, **kwargs):
    if created:
        NotificationPreferences.objects.create(user=instance)
