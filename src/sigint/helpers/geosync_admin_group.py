from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance: User, created, **kwargs):
    if created and instance.is_superuser:
        instance.groups.add(Group.objects.get(name='group_name'))