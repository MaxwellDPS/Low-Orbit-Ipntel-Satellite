from datetime import timedelta
from io import BytesIO
import logging
import traceback
from pathlib import Path

from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
from django_db_geventpool.utils import close_connection

from sigint.models import GeoSync

import hashlib
import requests
import tarfile


class GEOFetchException(Exception):
    """
    Exception for failed geo update
    """

class GEOFileVerification(Exception):
    """
    Exception for failed geo update
    """

class GeoUpdate(object):
    """
    Helper class for Geo Lookups
    """
    def __init__(self, tracking: GeoSync = None) -> None:
        self.max_mind_key: str  = settings.MAX_MIND_KEY
        self.geoip_path: Path   = settings.GEOIP_PATH

        self.max_mind_urls = {
            "asn": {
                "url": f"https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-ASN&license_key={self.max_mind_key}&suffix=tar.gz",
                "name": "GeoLite2-ASN.mmdb"
            },
            "city": {
                "url": f"https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key={self.max_mind_key}&suffix=tar.gz",
                "name": "GeoLite2-City.mmdb"
            },
            "country": {
                "url": f"https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-Country&license_key={self.max_mind_key}&suffix=tar.gz",
                "name": "GeoLite2-Country.mmdb"
            }
        }
        self._tracker: GeoSync = tracking

    def _validate_file(self, sha_256: str, data: BytesIO) -> bool:
        """
        SHA256 this s***
        """
        computed = hashlib.sha256(data).hexdigest()
        if sha_256 != computed:
            raise GEOFileVerification(f"GOT {computed} EXPECTED {sha_256}")

    def _untar(self, tar: BytesIO) -> BytesIO:
        """
        Summon the tar godz
        """
        with tarfile.open(fileobj=BytesIO(tar), mode="r|gz") as file:
            for member in file:
                if 'mmdb' in member.name:
                    return file.extractfile(member)

    def _pull_file(self, file_url: str, verify: bool = True, retry: int = 20, stream: bool = True) -> bytes:
        """
        Does a thing 
        """
        file = None
        headers = {
            'User-Agent': settings.GEO_SYNC_USERAGENT,
        }
        response = requests.get(file_url, stream=stream,  verify=verify, timeout=30, headers=headers)
        if response.status_code == 200:
            if stream:
                file = response.raw
            else:
                file = response.text

        number_of_potatos = 0
        while not response.ok:
            number_of_potatos += 1
            response = requests.get(file_url, stream=stream,  verify=verify, timeout=30, headers=headers)

            if number_of_potatos >= retry:
                raise GEOFetchException(f"Failed to Fetch - {file_url}")
            
        if response.status_code == 200:
            if stream:
                file = response.raw
            else:
                file = response.text

        return file

    @close_connection
    def start_sat_uplink(self) -> None:
        """
        Execute Geo Sync Actionz
        """
        try:
            self._tracker.status='in_progress'
            self._tracker.save()
            lastsync = None
            syncs =  GeoSync.objects.filter(time__gte=timezone.now() - timedelta(days=7))
            if syncs.exists():
                for sync in syncs:
                    sync.rollover()
                
            for db_type, db_meta in self.max_mind_urls.items():
                tar_data = self._pull_file(db_meta["url"])
                tar_data = tar_data.read()

                sha_data = self._pull_file(db_meta["url"] + '.sha256', stream=False)
                sha_256 = sha_data.split(' ')[0].strip()

                self._validate_file(sha_256=sha_256, data=tar_data)
                db_name = db_meta["name"]
                data = self._untar(tar_data)

                if db_type == "asn":
                    self._tracker.asn_hash = sha_256
                    self._tracker.asn_file = ContentFile(data.read(), name=db_name)
                    self._tracker.save()
                elif db_type == "city":
                    self._tracker.city_hash = sha_256
                    self._tracker.city_file = ContentFile(data.read(), name=db_name)
                    self._tracker.save()
                elif db_type == "country":
                    self._tracker.country_hash = sha_256
                    self._tracker.country_file = ContentFile(data.read(), name=db_name)
                    self._tracker.save()

            self._tracker.status = "success"
            self._tracker.latest = True
            self._tracker.save()
        except Exception as fire:
            
            self._tracker.status = "error"
            self._tracker.latest = False
            self._tracker.error_info = f'[ERROR 🔥] {fire}\n\n{traceback.format_exc()}'
            self._tracker.save()

            if syncs:
                for sync in syncs:
                    sync.recover()
                    return None

        
