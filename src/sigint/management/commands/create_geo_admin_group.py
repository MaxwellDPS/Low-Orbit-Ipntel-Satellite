from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from django.conf import settings

class Command(BaseCommand):
    help = "Makes the default Geo Admin group"

    def handle(self, *args, **options):
        self.config_geo_admin_group()

    def config_geo_admin_group(self) -> None:
        """
        Sets up Geo Admin group
        """
        if not Group.objects.filter(name=settings.GEO_SYNC_ADMIN_GROUP):
            Group(
                name=settings.GEO_SYNC_ADMIN_GROUP
            ).save()
