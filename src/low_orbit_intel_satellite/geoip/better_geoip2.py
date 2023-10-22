"""
YES 👉
"""
import logging
import socket

import geoip2.errors

from pathlib import Path

import geoip2.records
import geoip2.database

from django.conf import settings
from django.utils._os import to_path
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv46_address

from low_orbit_intel_satellite.geoip.helpers import (
    ASN, City, Country, GeoIP2Exception
)

from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network, ip_address, ip_network

NET_TYPEZ = IPv6Network | IPv4Network
ADDR_TYPEZ = IPv4Address | IPv6Address

GEOIP_SETTINGS = {
    "GEOIP_PATH": getattr(settings, "GEOIP_PATH", None),
    "GEOIP_CITY": getattr(settings, "GEOIP_CITY", "GeoLite2-City.mmdb"),
    "GEOIP_COUNTRY": getattr(settings, "GEOIP_COUNTRY", "GeoLite2-Country.mmdb"),
    "GEOIP_ASN": getattr(settings, "GEOIP_ASN", "GeoLite2-ASN.mmdb"),
}

class GeoIP2:
    """
    Django GeoIP2 Fixed... @Django fix your s***... like gooooooood damn 
    """
    # The flags for GeoIP memory caching.
    # Try MODE_MMAP_EXT, MODE_MMAP, MODE_FILE in that order.
    MODE_AUTO, MODE_MMAP_EXT, MODE_MMAP, MODE_FILE, MODE_MEMORY = 0, 1, 2, 4, 8
    cache_options = frozenset(
        (MODE_AUTO, MODE_MMAP_EXT, MODE_MMAP, MODE_FILE, MODE_MEMORY)
    )

    # Paths to the city & country binary databases.
    _city_file,_country_file,_asn_file = "", "", ""

    # Initially, pointers to GeoIP file references are NULL.
    _city, _country, _asn  = None, None, None

    def __init__(self, path: Path = None, cache: int = 0, country: str = None, city: str = None, asn: str = None) -> None:
        """
        Initialize the GeoIP object. No parameters are required to use default
        settings. Keyword arguments may be passed in to customize the locations
        of the GeoIP datasets.

        * path: Base directory to where GeoIP data is located or the full path
            to where the city or country data files (*.mmdb) are located.
            Assumes that both the city and country data sets are located in
            this directory; overrides the GEOIP_PATH setting.

        * cache: The cache settings when opening up the GeoIP datasets. May be
            an integer in (0, 1, 2, 4, 8) corresponding to the MODE_AUTO,
            MODE_MMAP_EXT, MODE_MMAP, MODE_FILE, and MODE_MEMORY,
            `GeoIPOptions` C API settings,  respectively. Defaults to 0,
            meaning MODE_AUTO.

        * country: The name of the GeoIP country data file. Defaults to
            'GeoLite2-Country.mmdb'; overrides the GEOIP_COUNTRY setting.

        * city: The name of the GeoIP city data file. Defaults to
            'GeoLite2-City.mmdb'; overrides the GEOIP_CITY setting.

        * asn: The name of the GeoIP ASN data file. Defaults to
            'GeoLite2-ASN.mmdb'; overrides the GEOIP_ASN setting.
        """
        # Checking the given cache option.
        if cache not in self.cache_options:
            raise GeoIP2Exception(f"Invalid GeoIP caching option: {cache}")

        # Getting the GeoIP data path.
        path = path or GEOIP_SETTINGS["GEOIP_PATH"]
        if not path:
            raise GeoIP2Exception(
                "GeoIP path must be provided via parameter or the GEOIP_PATH setting."
            )

        path = to_path(path)
        if path.is_dir():
            # Constructing the GeoIP database filenames using the settings
            # dictionary. If the database files for the GeoLite country
            # and/or city datasets exist, then try to open them.
            country_db = path / (country or GEOIP_SETTINGS["GEOIP_COUNTRY"])
            if country_db.is_file():
                self._country = geoip2.database.Reader(str(country_db), mode=cache)
                self._country_file = country_db

            city_db = path / (city or GEOIP_SETTINGS["GEOIP_CITY"])
            if city_db.is_file():
                self._city = geoip2.database.Reader(str(city_db), mode=cache)
                self._city_file = city_db
            if not self._reader:
                raise GeoIP2Exception(f"Could not load CITY database from {path}.")

            asn_db = path / (asn or GEOIP_SETTINGS["GEOIP_ASN"])
            if asn_db.is_file():
                self._asn = geoip2.database.Reader(str(asn_db), mode=cache)
                self._asn_file = asn_db
            if not self._reader:
                raise GeoIP2Exception(f"Could not load ASN database from {path}.")

        elif path.is_file():
            # Otherwise, some detective work will be needed to figure out
            # whether the given database path is for the GeoIP country or city
            # databases.
            reader = geoip2.database.Reader(str(path), mode=cache)
            db_type = reader.metadata().database_type

            if "City" in db_type:
                # GeoLite City database detected.
                self._city = reader
                self._city_file = path
            elif "Country" in db_type:
                # GeoIP Country database detected.
                self._country = reader
                self._country_file = path
            elif "ASN" in db_type:
                # GeoIP Country database detected.
                self._asn = reader
                self._asn_file = path
            else:
                raise GeoIP2Exception(
                    f"Unable to recognize database edition: {db_type}"
                )
        else:
            raise GeoIP2Exception("GeoIP path must be a valid file or directory.")

    @property
    def _reader(self):
        if self._asn:
            return self._asn
        elif self._city:
            return self._city
        elif self._country:
            return self._country
        return None

    @property
    def _country_or_city(self):
        if self._country:
            return self._country.country
        else:
            return self._city.city

    def __del__(self) -> None:
        # Cleanup any GeoIP file handles lying around.
        if self._reader:
            self._reader.close()

    def __repr__(self) -> str:
        meta = self._reader.metadata()
        version = f"[v{meta.binary_format_major_version}.{meta.binary_format_minor_version}]"
        return f'<{self.__class__.__name__} {version} _country_file="{self._country_file}", _city_file="{self._city_file}", _asn_file="{self._asn_file}">'

    def _check_query(self, query, asn=False, city=False, city_or_country=False) -> str:
        "Check the query and database availability."
        # Making sure a string was passed in for the query.
        if not isinstance(query, (str,ADDR_TYPEZ)) :
            raise TypeError(
                f"GeoIP query must be a string, not type {type(query).__name__}" 
            )

        if isinstance(query, ADDR_TYPEZ):
            query = query.compressed

        # Extra checks for the existence of country and city databases.
        if city_or_country and not (self._country or self._city):
            raise GeoIP2Exception("Invalid GeoIP country and city data files.")
        elif city and not self._city:
            raise GeoIP2Exception(f"Invalid GeoIP city data file: {self._city_file}")

        # Check for ASN databases
        if asn and not self._asn:
            raise GeoIP2Exception(f"Invalid GeoIP ASN data file: {self._asn_file}")

        # Return the query string back to the caller. GeoIP2 only takes IP addresses.
        try:
            validate_ipv46_address(query)
        except ValidationError:
            query = socket.gethostbyname(query)

        return query

    def asn(self, query) -> ASN:
        """
        Return a dictionary of city information for the given IP address or
        Fully Qualified Domain Name (FQDN). Some information in the dictionary
        may be undefined (None).
        """
        enc_query = self._check_query(query, asn=True)
        try:
            return ASN(self._asn.asn(enc_query))
        except geoip2.errors.AddressNotFoundError as err:
            return None

    def city(self, query) -> City:
        """
        Return a dictionary of city information for the given IP address or
        Fully Qualified Domain Name (FQDN). Some information in the dictionary
        may be undefined (None).
        """
        enc_query = self._check_query(query, city=True)
        return City(self._city.city(enc_query))

    def country_code(self, query) -> int:
        "Return the country code for the given IP Address or FQDN."
        return self.country(query).iso_code

    def country_flag(self, query) -> str:
        "Return the country code for the given IP Address or FQDN."
        return self.country(query).flag

    def country_name(self, query) -> str:
        "Return the country name for the given IP Address or FQDN."
        return self.country(query).name

    def country(self, query) -> Country:
        """
        Return a dictionary with the country code and name when given an
        IP address or a Fully Qualified Domain Name (FQDN). For example, both
        '24.124.1.80' and 'djangoproject.com' are valid parameters.
        """
        # Returning the country code and name
        enc_query = self._check_query(query, city_or_country=True)
        return Country(self._country_or_city(enc_query))

    # #### Coordinate retrieval routines ####
    def coords(self, query, ordering: tuple = ("longitude", "latitude")) -> tuple[float]:
        """
        Retuns a lat long pair as a tuple
        """
        c_object = self.city(query)
        if c_object is None:
            return None
        else:
            thingy = tuple()
            for why in ordering:
                thingy = thingy + tuple(c_object.__getattribute__(why))
            return thingy

    def lon_lat(self, query) -> tuple[float]:
        "Return a tuple of the (longitude, latitude) for the given query."
        return self.coords(query)

    def lat_lon(self, query) -> tuple[float]:
        "Return a tuple of the (latitude, longitude) for the given query."
        return self.coords(query, ("latitude", "longitude"))

    def geos(self, query):
        "Return a GEOS Point object for the given query."
        long_lat = self.lon_lat(query)
        if long_lat:
            # Allows importing and using GeoIP2() when GEOS is not installed.
            from django.contrib.gis.geos import Point

            return Point(long_lat, srid=4326)
        else:
            return None

    # #### GeoIP Database Information Routines ####
    @property
    def info(self) -> str:
        "Return information about the GeoIP library and databases in use."
        meta = self._reader.metadata()
        return f"Better GeoIP Library:\n\t{meta.binary_format_major_version}.{meta.binary_format_minor_version}\n"

    @classmethod
    def open(cls, full_path, cache):
        return GeoIP2(full_path, cache)
