from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from sigint.models import (
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
    readonly_fields = ('uuid',)
    list_display = (
        'name',
        'uuid',
        'enabled',
        'expires',
        'throttle_rate',
        'allow_cidr_lookups',
        'client'
    )
    search_fields = ('uuid', 'name')
    list_filter = ('enabled','expires','allow_cidr_lookups')


@admin.register(LookupRequest)
class LookupRequestAdmin(admin.ModelAdmin):
    """
    Admin class for the LookupRequest
    """
    readonly_fields = ('uuid', 'time', 'user', 'status', 'valid_lookups', 'error_info')
    ordering = ('time',)
    list_display = (
        'uuid',
        'time',
        'user',
        'valid_lookups',
        'status'
    )
    search_fields = ('uuid', 'user')
    list_filter = ('user','time','status')

class ValidListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("Valid")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "valid"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [
            ("true", _("True")),
            ("false", _("False")),
        ]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == "false":
           return queryset.filter(
                valid_until__lte= timezone.now(),
            ) 
        if self.value() == "true":
            return queryset.filter(
                valid_until__gte= timezone.now(),
            )


@admin.register(AddressResult)
class AddressResultAdmin(admin.ModelAdmin):
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
        'valid_from',
        'valid_until',
    )
    search_fields = ('uuid', 'autonomous_system_organization', 'ip_address', 'city_name', 'region_name', 'country_name', 'autonomous_system_number', 'continent_code','region_code', 'country_code' )
    list_filter = ('bogon', ValidListFilter, 'valid_from', 'matches_lists', 'country_european_union', 'continent_name' )

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
                "fields": ["valid_from", "valid_until"],
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
                "fields": [("country_flag", "country_name"), "country_european_union", "country_code", "country_confidence"],
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
                "fields": ["city_name", "city_confidence", "metro_code"],
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

class ValidGeoSyncFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("Valid")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "valid"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [
            ("true", _("True")),
            ("false", _("False")),
        ]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == "false":
           return queryset.filter(
                expires__lte= timezone.now(),
            ) 
        if self.value() == "true":
            return queryset.filter(
                expires__gte= timezone.now(),
            )


@admin.register(GeoSync)
class GeoSyncAdmin(admin.ModelAdmin):
    """
    Admin class for the AccessPlan
    """
    readonly_fields = (
        'uuid',
        'celery_task',
        'celery_task_uuid',
        'time',
        'status',
        'asn_hash',
        'city_hash',
        'country_hash',
        'latest',
        'asn_file',
        'city_file',
        'country_file',
        'expires',
        'error_info'
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
    search_fields = ('uuid', 'celery_task_uuid', 'city_hash','asn_hash','country_hash')
    list_filter = (ValidGeoSyncFilter, 'latest', 'status','time')

    fieldsets = [
        (
            None,
            {
                "fields": ["uuid", "time", "status", "latest", "expires", ('celery_task','celery_task_uuid'), "error_info"],
            },
        ),
        (
            "Files",
            {
                "classes": [],
                "fields": [
                    ("asn_hash", "asn_file"),
                    ("city_hash", "city_file"),
                    ("country_hash", "country_file"),
                ],
            },
        ),
    ]

    def save_model(self, request, obj, form, change):
        obj.save()
        from sigint.tasks import run_geo_window
        run_geo_window.delay(geo_sync_id=obj.uuid)
        