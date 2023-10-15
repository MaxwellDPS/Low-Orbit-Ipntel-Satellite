import io
import traceback
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from skynet.models import GeoSync

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

    def _validate_file(self, sha_256: str, data: bytes) -> bool:
        """
        SHA256 this s***
        """
        computed = hashlib.sha256(data).hexdigest()
        if sha_256 != computed:
            raise GEOFileVerification(f"GOT {computed} EXPECTED {sha_256}")

    def _untar(self, tar: bytes, db_file_name: str) -> bytes:
        """
        Summon the tar godz
        """
        with tarfile.open(io.BytesIO(tar), "r:gz") as file:
            return file.extractfile(db_file_name).read()

    def _pull_file(self, file_url: str, verify: bool = True, retry: int = 20) -> bytes:
        """
        Does a thing 
        """
        data = requests.get(file_url, \
            verify=verify, timeout=30, user_agent=settings.GEO_SYNC_USERAGENT)

        number_of_potatos = 0
        while not data.ok:
            number_of_potatos += 1
            data = requests.get(file_url, verify=verify, timeout=30)

            if number_of_potatos >= retry:
                raise GEOFetchException(f"Failed to Fetch - {file_url}")

        return data.content

    def start_sat_uplink(self) -> None:
        """
        Execute Geo Sync Actionz
        """
        try:
            self._tracker.status='in_progress'
            self._tracker.save()
            for db_type, db_meta in self.max_mind_urls.items():
                tar_data = self._pull_file(db_meta["url"])

                sha_data = self._pull_file(db_meta["url"] + '.sha256').decode("utf-8")
                sha_256 = sha_data.split(' ')[0].trim()

                db_name = db_meta["name"]

                self._validate_file(sha_256=sha_256, data=tar_data)
                data = self._untar(tar_data, db_name)

                if db_type == "asn":
                    self._tracker.asn_hash = sha_256
                    self._tracker.asn_file = ContentFile(data, name=db_name)
                elif db_type == "city":
                    self._tracker.city_hash = sha_256
                    self._tracker.city_file = ContentFile(data, name=db_name)
                elif db_type == "country":
                    self._tracker.country_hash = sha_256
                    self._tracker.country_file = ContentFile(data, name=db_name)

            self._tracker.status = "success"
            self._tracker.latest = True
        except Exception as err:
            self._tracker.status = "error"
            self._tracker.error_info = f'[ERROR] {err}\n\n{traceback.format_exc()}'

        self._tracker.save()
