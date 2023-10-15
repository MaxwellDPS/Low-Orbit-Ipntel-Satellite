from django.contrib import admin

from skynet.models import (
    LookupRequest,
    AddressResult,
    AccessPlan,
    GeoSync
)

@admin.register(AccessPlan)
class AccessPlanAdmin(admin.ModelAdmin):
    """
    Admin class for the AccessPlan
    """
    readonly_fields = ('uuid', 'time', 'user', 'response_type', 'valid_lookups')
    ordering = ('time',)
    list_display = (
        'uuid',
        'enabled',
        'starts',
        'expires',
        'rate_limit_requests_per_min',
        'allowed_lookups_per_day',
        'allowed_lookups_per_month',
        'allow_cidr_lookups'
    )
    search_fields = ('uuid', 'user')
    list_filter = ('user','time','response_type')


@admin.register(LookupRequest)
class LookupRequestAdmin(admin.ModelAdmin):
    """
    Admin class for the LookupRequest
    """
    readonly_fields = ('uuid', 'time', 'user', 'response_type', 'valid_lookups')
    ordering = ('time',)
    list_display = (
        'uuid',
        'time',
        'user',
        'valid_lookups',
        'response_type'
    )
    search_fields = ('uuid', 'user')
    list_filter = ('user','time','response_type')


@admin.register(AddressResult)
class AddressResultSerializer(admin.ModelAdmin):
    """
    Admin class for the LookupRequest
    """
    readonly_fields = ('uuid',)
    ordering = ('valid_from',)
    list_display = (
        'uuid',
        'lookup',
        'ip_address',
        'bogon',
        'country_flag',
        'city_name',
        'region_name',
        'country_name',
        'postal_code',
        'latitude',
        'longitude',
        'autonomous_system_number',
        'autonomous_system_organization',
        'valid'
        'valid_from',
        'valid_until',
    )
    search_fields = ('uuid', 'autonomous_system_organization', 'ip_address', 'city_name', 'region_name', 'country_name', 'autonomous_system_number', 'continent_code','region_code', 'country_code' )
    list_filter = ('bogon','valid', 'valid_from', 'matches_lists', 'country_european_union', 'continent_name' )

    fieldsets = [
        (
            None,
            {
                "fields": ["uuid", "lookup", "ip_address", "ip_version", "accuracy_radius"],
            },
        ),
        (
            "Validity",
            {
                "classes": [],
                "fields": ["valid", "valid_from", "valid_until"],
            },
        ),
        (
            "Autonomous System",
            {
                "classes": ["collapse"],
                "fields": ["autonomous_system_organization", "autonomous_system_number"],
            },
        ),
        (
            "Continent",
            {
                "classes": ["collapse"],
                "fields": ["continent_name", "continent_code"],
            },
        ),
         (
            "Country",
            {
                "classes": ["collapse"],
                "fields": [("country_flag", "country_name"), "european_union", "country_code", "country_confidence"],
            },
        ),
        (
            "Region",
            {
                "classes": ["collapse"],
                "fields": [("region_flag", "region_name"), "region_code", "region_confidence"],
            },
        ),
        (
            "City",
            {
                "classes": ["collapse"],
                "fields": ["name", "confidence", "metro_code"],
            },
        ),
         (
            "Demographics",
            {
                "classes": ["collapse"],
                "fields": ["timezone", ("postal_code", "postal_confidence"), ("latitude", "longitude"), "population_density", "average_income"],
            },
        ),
    ]

@admin.register(GeoSync)
class GeoSyncAdmin(admin.ModelAdmin):
    """
    Admin class for the AccessPlan
    """
    readonly_fields = (
        'uuid',
        'celery_task',
        'celery_task_id',
        'time',
        'status',
        'asn_hash',
        'city_hash',
        'country_hash',
        'latest',
        'asn_file',
        'city_file',
        'country_file',
        'expires'
    )
    ordering = ('time',)
    list_display = (
        'time',
        'status',
        'latest',
        'expires',
        'asn_hash',
        'city_hash',
        'country_hash',
    )
    search_fields = ('uuid', 'celery_task_id', 'city_hash','asn_hash','country_hash')
    list_filter = ('latest', 'status','time')

    fieldsets = [
        (
            None,
            {
                "fields": ["uuid", "time", "status", "latest", ("expired", "expires"), ('celery_task','celery_task_id')],
            },
        ),
        (
            "Files",
            {
                "classes": [],
                "fields": [
                    ("asn_hash", "asn_file"),
                    ("city_file", "city_file"),
                    ("country_file", "country_file"),
                ],
            },
        ),
    ]

    def save_model(self, request, obj, form, change):
        obj.save()
        from skynet.tasks import run_geo_window
        run_geo_window.delay(geo_sync=obj)
        