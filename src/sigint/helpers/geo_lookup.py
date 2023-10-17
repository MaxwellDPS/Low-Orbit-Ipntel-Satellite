import logging
import traceback
import uuid

from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network, ip_address, ip_network

from django.db.models import Q
from django.db.models import signals
from django.contrib.auth.models import User

from django_db_geventpool.utils import close_connection

from sigint.models import AddressResult, LookupRequest, AccessPlan
from low_orbit_intel_satellite.geoip.better_geoip2 import GeoIP2, City, ASN


NET_TYPEZ = IPv6Network | IPv4Network
ADDR_TYPEZ = IPv4Address | IPv6Address
SOMETHING_LIKELY_STUPID = str | NET_TYPEZ | ADDR_TYPEZ | list[NET_TYPEZ|ADDR_TYPEZ|str]


class GeoCheck(object):
    """
    Helper class for Geo Lookups
    """
    def __init__(self, lookup_request: LookupRequest) -> None:
        self.geo_lookupz                            = GeoIP2()
        self.valid: int                             = 0
        self.invalid: int                           = 0
        self._results: dict                         = {}
        self.user: User                             = lookup_request.user
        self.raw_address:SOMETHING_LIKELY_STUPID    = None
        self.lookup_request: LookupRequest          = lookup_request
        self.allow_cidr_lookup: bool                = self.allowed_cidr()

    def allowed_cidr(self) -> bool:
        """
        Check if user has a plan that allows cidsr lookups
        """
        plans = AccessPlan.objects.filter(Q(users=self.user)|Q(groups__in=self.user.groups.all()))
        plans = plans.filter(allow_cidr_lookups=True)
        return plans.count() > 0


    def _validate_ip(self, address: str | ADDR_TYPEZ) -> None:
        if isinstance(address, ADDR_TYPEZ):
            self._results[address] = {
                "valid": True,
                "raw": address,
                "value": address
            }
            self.valid += 1
        else:
            try:
                value = ip_address(address)
                
                self._results[value.compressed] = {
                    "valid": True,
                    "raw": address,
                    "value": value
                }
                self.valid += 1
            except Exception as err:
                self._results[address] = {
                    "valid": False,
                    "raw": address,
                    "error": {
                        "type": "validation",
                        "error":  err,
                    }
                }
                self.invalid += 1

    def _sanitize_expand_load(self, input_ip: str | NET_TYPEZ | ADDR_TYPEZ ) -> None:
        if isinstance(input_ip, NET_TYPEZ):
            if self.allow_cidr_lookup:
                for address in input_ip.hosts():
                    self._validate_ip(address)
            else:
                self._results[input_ip.compressed] = {
                    "valid": False,
                    "raw": str(input_ip),
                    "error": {
                        "type": "cidr-not-allowded",
                        "error":  "NOT ALLOWED TODO CIDR LOOKUPS",
                    }
                }
                self.invalid += 1
        elif isinstance(input_ip, str):
            if '/' in input_ip:
                ip, cidr = input_ip.split('/')
                if cidr in ['32', '128']:
                    self._validate_ip(ip)
                else:
                    try:
                        self._sanitize_expand_load(ip_network(input_ip))
                    except Exception as err:
                        self._results[input_ip] = {
                            "valid": False,
                            "raw": input_ip,
                            "error": {
                                "type": "validation",
                                "error": err,
                            }
                        }
                        self.invalid += 1
            else:
                self._validate_ip(input_ip)
        else:
            self._validate_ip(input_ip)

    def _check_all(self) -> None:
        if isinstance(self.raw_address, str | NET_TYPEZ | ADDR_TYPEZ):
            self._sanitize_expand_load(self.raw_address)
        elif isinstance(self.raw_address, list):
            for lookup in self.raw_address:
                self._sanitize_expand_load(lookup)

    def _make_orm_instance(
        self,
        lookup_request: LookupRequest,
        address: NET_TYPEZ,
        asn: ASN,
        city: City
    ) -> AddressResult:
        address = AddressResult(
            lookup = lookup_request,
            ip_address = address.compressed,
            autonomous_system_organization = asn.autonomous_system_organization,
            autonomous_system_number = asn.autonomous_system_number,
            postal_code = city.postal_code.code,
            postal_confidence = city.postal_code.confidence,
            average_income = city.average_income,
            accuracy_radius = city.accuracy_radius,
            latitude = city.latitude,
            longitude = city.longitude,
            population_density = city.population_density,
            timezone = city.time_zone,
            city_name = city.name,
            city_confidence = city.confidence,
            metro_code = city.metro_code,
            region_name = city.region.name if city.region else None,
            region_flag = city.region.flag if city.region else None,
            region_code = city.region.iso_code if city.region else None,
            region_confidence = city.region.confidence  if city.region else None,
            country_name = city.country.name,
            country_flag = city.country.flag,
            country_european_union = city.country.european_union,
            country_code = city.country.iso_code,
            country_confidence = city.country.confidence
        )
        return address

    @close_connection
    def _bulk_load(self, objects: list[AddressResult]) -> list[uuid.UUID]:
        AddressResult.objects.bulk_create(objects)
        loaded = []
        for i in objects:
            signals.post_save.send(i.__class__, instance=i, created=True)
            loaded.append(i.uuid)
        return loaded

    def _lookup(self, address: str) -> tuple[City,ASN]:
        """
        Runs the geo lookups
        """
        return self.geo_lookupz.city(address), self.geo_lookupz.asn(address)

    def _collect_errors(self) -> dict:
        errors = {}

        for k, v in self._results.items():
            if not v["valid"]:
                errors[k] = v

        return errors

    @close_connection
    def run(self, requested: SOMETHING_LIKELY_STUPID) -> tuple[any,dict]:
        """
        Entrypoint for lookup
        """
        try:
            self.raw_address = requested
            self.lookup_request.status = "in_progress"
            self.lookup_request.save()

            # Validate and populate _results
            self._check_all()

            results = []
            found = []
            
            for data in self._results.values():
                if not data["valid"]:
                    continue
                addr = data["value"]

                # existing = AddressResult.objects.filter(ip_address=addr.compressed, valid_until__gte=timezone.now())
                # if not existing.exists():
                city, asn = self._lookup(str(addr))
                results.append(self._make_orm_instance(
                    lookup_request=self.lookup_request,
                    address=addr,
                    asn=asn,
                    city=city
                ))
                # else:
                #     found.append(existing.first().uuid)

            logging.info(f"[💽] {self.lookup_request.uuid} SAVING {len(results)} ADDRESS RESULTS TO BASE")
            created_ids = self._bulk_load(results)
            address_qs = AddressResult.objects.filter(uuid__in=created_ids+found)

            errors = self._collect_errors()
            self.lookup_request.invalid_lookups = errors
            self.lookup_request.status = "success"
            self.lookup_request.valid_lookups = self.valid
            self.lookup_request.save()
            return address_qs, errors
        except Exception as fire:
            self.lookup_request.error_info = traceback.format_exc()
            self.lookup_request.status = "error"
            self.lookup_request.valid_lookups = self.valid
            self.lookup_request.save()
            raise fire
