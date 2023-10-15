from rest_framework import serializers
from skynet.models import (
    LookupRequest,
    AddressResult,
    CIDRTagsList,
    GeoSync
)

# pylint: disable = missing-class-docstring
class CIDRTagsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CIDRTagsList
        fields = [
            'uuid'
        ]

class GeoSyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeoSync
        fields = [
            'uuid',
            'celery_task_id',
            'time',
            'expired',
            'expires',
            'status',
            'asn_hash',
            'city_hash',
            'country_hash',
            'error_info',
            'latest',
        ]

    def to_representation(self, instance: GeoSync):
        """
        Make it fancy
        """
        payload = {
            "uuid": str(instance.uuid),
            "time": instance.time.isoformat(),
            "expired": instance.expired,
            "expires": instance.expires.isoformat(),
            "status": instance.status.isoformat(),
            "latest": instance.status.isoformat(),
            "error_info": instance.status.isoformat(),
            "files": {
               "asn": {
                   "hash": instance.asn_hash,
                   "url": instance.asn_file.url,
               },
               "city": {
                   "hash": instance.city_hash,
                   "url": instance.city_file.url,
               },
               "country": {
                   "hash": instance.country_hash,
                   "url": instance.country_file.url,
               }
            }
        }
        return payload

class AddressResultSerializer(serializers.ModelSerializer):
    matches_lists = CIDRTagsList(many=True)

    class Meta:
        model = AddressResult
        fields = [
            'uuid',
            'lookup',
            'valid',
            'valid_from',
            'valid_until',
            'ip_address',
            'ip_version',
            'autonomous_system_organization',
            'autonomous_system_number',
            'postal_code',
            'postal_confidence',
            'average_income',
            'accuracy_radius',
            'latitude',
            'longitude',
            'population_density',
            'timezone',
            'city_name',
            'city_confidence',
            'metro_code',
            'region_name',
            'region_flag',
            'region_code',
            'region_confidence',
            'country_name',
            'country_flag',
            'country_european_union',
            'country_code',
            'country_confidence',
            'continent_name',
            'continent_code',
            'matches_lists',
            'bogon'
        ]

    def to_representation(self, instance: AddressResult):
        """
        Make it fancy
        """
        payload = {
            "uuid": str(instance.uuid),
            "validity": {
                "valid": instance.valid,
                "valid_from": instance.valid_from.isoformat(),
                "valid_until": instance.valid_from.isoformat()
            },
            "lookup":{
                "address": {
                    "value": str(instance.ip_address),
                    "version": instance.ip_version,
                    "bogon": instance.bogon
                }
            },
            "result": {
                "autonomous_system": {
                    "organization": instance.autonomous_system_organization,
                    "number": instance.autonomous_system_number,
                },
                "geoip":{
                    "accuracy_radius": instance.accuracy_radius,
                    "timezone": instance.timezone,
                    "city": {
                        "name": instance.city_name,
                        "confidence": instance.city_confidence,
                        "metro_code": instance.metro_code
                    },
                    "region": {
                        "name": instance.region_name,
                        "flag": instance.region_flag,
                        "code": instance.region_code,
                        "region": instance.region_confidence,
                    },
                    "country": {
                        "name": instance.country_name,
                        "flag": instance.country_flag,
                        "european_union": instance.country_european_union,
                        "code": instance.country_code,
                        "confidence": instance.country_confidence
                    },
                    "continent":{
                        "name": instance.continent_name,
                        "code": instance.continent_code,
                        
                    },
                    "postal": {
                        "code": instance.postal_code,
                        "confidence": instance.postal_confidence,
                    },
                    "coordinates":{
                        "latitude": instance.latitude,
                        "longitude": instance.longitude,
                    },
                    "demographics":{
                        "population_density": instance.population_density,
                        "average_income": instance.average_income
                    }
                },
                "tag_matches": []
            }
        }
        return payload

class LookupRequestSerializer(serializers.ModelSerializer):
    valid_lookups = AddressResultSerializer(many=True, read_only=True)

    class Meta:
        model = LookupRequest
        fields = [
            'uuid',
            'time',
            'user',
            'valid_lookups',
            'invalid_lookups',
            'response_type'
        ]
