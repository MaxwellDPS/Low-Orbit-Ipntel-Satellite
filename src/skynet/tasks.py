"""
 _________________ 
< Multitasking yo >
 ----------------- 
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
"""
import uuid

from django.contrib.auth.models import User
from celery import shared_task
from skynet.models import GeoSync, LookupRequest


@shared_task(bind=True)
def sync_maxmind_database(self, sync_uuid: uuid.UUID = None, force: bool = False) -> None:
    """
    Celery Task to Sync Max Mind Data bases
    """
    from skynet.helpers.geo_update import GeoUpdate

    valid_syncs = GeoSync.objects.filter(expired=False)
    if valid_syncs and not force:
        # We gucci
        return None

    if not sync_uuid:
        sync_uuid = uuid.uuid4()

    current_sync :GeoSync = GeoSync.objects.create(
        celery_task_id=uuid.UUID(self.request.id),
        uuid=sync_uuid
    )
    sync_it_real_good: GeoUpdate = GeoUpdate(tracking=current_sync)
    sync_it_real_good.start_sat_uplink()

@shared_task(bind=True)
def run_geo_window(self, geo_sync: GeoSync) -> None:
    """
    Celery Task to Sync Max Mind Data bases
    """
    from skynet.helpers.geo_update import GeoUpdate

    geo_sync.celery_task_id=uuid.UUID(self.request.id)
    geo_sync.save()
    sync_it_real_good: GeoUpdate = GeoUpdate(tracking=geo_sync)
    sync_it_real_good.start_sat_uplink()

@shared_task(bind=True)
def run_geo_lookup(self, request_uuid: uuid.UUID, requested_ips: list[str]) -> None:
    """
    Celery Task to Sync Max Mind Data bases
    """
    from skynet.helpers.geo_lookup import GeoCheck

    lookup_request = LookupRequest.objects.get(
        uuid=request_uuid,
    )
    checker = GeoCheck(lookup_request=lookup_request)
    checker.run(requested=requested_ips)


@shared_task(bind=True)
def prune(self) -> None:
    """
    Celery Task to Sync Max Mind Data bases
    """
    from skynet.helpers import prune_utils
    prune_utils.prune_geo()
    prune_utils.prune_ip_result()
    prune_utils.prune_lookup_requests()
   
@shared_task(bind=True)
def generate_lists(self) -> None:
    """
    Celery Task to Generate the CIDR Tracking Lists
    """
    pass
