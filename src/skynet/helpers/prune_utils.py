"""
 _____________________________________
/ If it doesnt bring you joy, nuke it \
\ ☢️                                   /
 ------------------------------------- 
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
"""
from django.conf import settings
from django.utils import timezone
from skynet.models import GeoSync, LookupRequest, AddressResult

def prune_geo():
    """
    yeet
    """
    GeoSync.objects.filter(
        expired=False
    ).delete()

def prune_lookup_requests():
    """
    yeet
    """
    LookupRequest.objects.filter(
        time__gte= (timezone.now() - settings.USER_LOOKUP_PRUNE_DAYS)
    ).delete()

def prune_ip_result():
    """
    yeet
    """
    AddressResult.objects.filter(
        valid_from__gte= (timezone.now() - settings.IP_GEO_CACHE_PRUNE_DAYS)
    ).delete()
