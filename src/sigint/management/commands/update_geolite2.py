import uuid
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from sigint.helpers.geo_update import GeoUpdate
from sigint.models import GeoSync

class Command(BaseCommand):
    help = "Resyncs Maxmind's GeoLite 2 Database"

    def add_arguments(self, parser):
        parser.add_argument('-f',"--force", action='store_true')

    def handle(self, *args, **options):
        force:bool = options["force"]
        sync_id = uuid.uuid4()
        self.sync_maxmind_database(sync_uuid=sync_id, force=force)


    def sync_maxmind_database(self, sync_uuid: uuid.UUID = None, force: bool = False) -> None:
        """
        Sync Max Mind Data bases
        """

        valid_syncs = GeoSync.objects.filter(expires__gte=timezone.now()).exclude(status='error')
        if valid_syncs and not force:
            self.stdout.write(
                self.style.WARNING(f"[{timezone.now().isoformat()}][NOT-UPDATED] ✅ MAXMIND DB VALID UNTILL {valid_syncs.first().expires.isoformat()}")
            )
            # We gucci
            return None

        try:
            if not sync_uuid:
                sync_uuid = uuid.uuid4()

            current_sync :GeoSync = GeoSync.objects.create(
                uuid=sync_uuid
            )
            sync_it_real_good: GeoUpdate = GeoUpdate(tracking=current_sync)
            sync_it_real_good.start_sat_uplink()
        except Exception as fire:
            self.stdout.write(
                self.style.ERROR(f"[{timezone.now().isoformat()}][ERROR] 🔥 FAILED TO SYNCED MAXMIND DB -- {str(fire)}")
            )
            return None

        self.stdout.write(
            self.style.SUCCESS(f"[{timezone.now().isoformat()}][SUCCESS] 🌐 SYNCED MAXMIND DB")
        )
