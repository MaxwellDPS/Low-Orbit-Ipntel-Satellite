"""
 __________________________________ 
< ALL THAT JUNK IN THE ~TRUNK~ ORM >
 ---------------------------------- 
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
"""
import logging
import os
from pathlib import Path
import uuid
import ipaddress
import datetime

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.dispatch import receiver
from django.db.models import signals
from django.contrib.auth.models import User, Group

from durin.models import Client 
from django_celery_results.models import TaskResult

TUESDAY = 1 # 0 = Monday, 1=Tuesday, 2=Wednesday...
def next_weekday(
    in_date: datetime.datetime,
    weekday,
    just_delta: bool = False
) -> datetime.datetime | datetime.timedelta:
    """
    Gets the next Tuesday or something who knows
    """
    days_ahead = weekday - in_date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    if just_delta:
        datetime.timedelta(days_ahead)
    return in_date + datetime.timedelta(days_ahead)

def get_upload_path(instance, filename):
    return f"/archived/{str(instance.time.year)}/{str(instance.time.month)}/{str(instance.time.day)}/{instance.uuid}/{filename}"

class CIDRTagsList(models.Model):
    """
    Tracked CIDRs
    """
    uuid = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4)

    def __str__(self):
        return str(self.uuid)

class ListGenerator(models.Model):
    """
    List Generator
    """

    uuid = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)

class AccessPlan(models.Model):
    """
    Model to track limits aginst a user
    """
    uuid = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255, blank=True, null=True)
    enabled = models.BooleanField(default=True, db_index=True)
    expires = models.DateTimeField(blank=True, null=True, db_index=True)

    groups = models.ManyToManyField(Group, blank=True)
    users = models.ManyToManyField(User, blank=True)

    throttle_rate = models.CharField(default="120/m", max_length=255)
    allow_cidr_lookups = models.BooleanField(default=True, db_index=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)

    def check_user_allowed(self, user: User) -> bool:
        """
        Checks if a user can use this plan
        """
        self.users: User
        if self.users.filter(pk=user.pk).exists():
            return True

        if user.groups.filter(name__in=self.groups.all().values_list('name', flat=True)).exists():
            return True
        
        return False

    @property
    def active(self) -> bool:
        """
        Check if Plan is active
        """
        if self.enabled and self.expires <= timezone.now():
            return True
        else:
            return False

class GeoSync(models.Model):
    """
    Model to track user requests
    """
    STATUS_CHOICES = (
        ('queued', "Queued ⌛"),
        ('in_progress','In Flight ✈️'),
        ('success','Success ✅'),
        ('error','Its On Fire 🔥'),

    )

    uuid = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4)
    celery_task = models.ForeignKey(TaskResult, on_delete=models.DO_NOTHING, null=True, blank=True)
    celery_task_uuid = models.UUIDField(null=True, blank=True)
    time = models.DateTimeField(default=timezone.now, db_index=True)
    expires = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='queued')
    asn_hash = models.CharField(max_length=255, blank=True, null=True)
    city_hash = models.CharField(max_length=255, blank=True, null=True)
    country_hash = models.CharField(max_length=255, blank=True, null=True)
    error_info = models.TextField(null=True, blank=True)
    latest = models.BooleanField(blank=True, null=True)

    STORAGE = getattr(settings,"GEOIP_STORAGE")

    asn_file = models.FileField(upload_to=get_upload_path, \
        null=True, blank=True, storage=STORAGE)
    city_file = models.FileField(upload_to=get_upload_path, \
        null=True, blank=True, storage=STORAGE)
    country_file = models.FileField(upload_to=get_upload_path, \
        null=True, blank=True, storage=STORAGE)

    @property
    def _expires(self) -> datetime.datetime:
        """
        Returns the experation
        """
        return next_weekday(self.time,TUESDAY)

    @property
    def expired(self) -> datetime.datetime:
        """
        Returns the experation
        """
        return self.time < (timezone.now() - settings.GEO_SYNC_PRUNE_DAYS)



    def rollover(self) -> None:
        """
        Archives files
        """

        for file_type in [self.asn_file, self.city_file, self.country_file]:
            try:
                file_type: models.FileField
                if not file_type:
                    continue
                if "archived" in file_type.path:
                    return None
                initial_path = Path(file_type.path)
                initial_name = file_type.name
                new_name = f"{self.time.isoformat()}_{self.uuid}_{initial_name}"
                new_path = f"{str(initial_path.parent)}/archived/{str(self.time.year)}/{str(self.time.month)}/{str(self.time.day)}/{new_name}"
                logging.error(new_path)
                new_path = Path(new_path)
                new_path.mkdir(exist_ok=True, parents=True)

                os.rename(initial_path, new_path)

                file_type.path = new_path
                file_type.name = new_name

                try:
                    os.remove(initial_path)
                except:
                    pass
            except Exception as err:
                logging.error(str(err))

            self.latest = False
            self.save()

    def recover(self) -> None:
        """
        Archives files
        """
        for file_type in [self.asn_file, self.city_file, self.country_file]:
            file_type: models.FileField
            initial_name = file_type.name
            initial_path = Path(file_type.path)

            new_path = Path(file_type.path.split('/archived/')[0])
            new_name = initial_name.split("_")[-1]

            os.rename(initial_path, new_path)

            file_type.path = new_path
            file_type.name = new_name

        self.latest = True
        self.save()

    def yeet(self) -> None:
        """
        Yeet files
        """
        for file_type in [self.asn_file, self.city_file, self.country_file]:
            file_type: models.FileField
            if not file_type:
                continue
            rip_homie = Path(file_type.path)
            if rip_homie.exists():
                os.remove(rip_homie)

    def __str__(self):
        return f"[{self.uuid}] {self.time} {self.status}"

    class Meta:
        """
        Django meta class
        """
        ordering = ["-time"]

class LookupRequest(models.Model):
    """
    Model to track user requests
    """

    STATUS_CHOICES = (
        ('queued', "Queued ⌛"),
        ('in_progress','In Flight ✈️'),
        ('success','Success ✅'),
        ('error','[ERROR] Somethings on Fire 🔥'),
    )

    uuid = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4)
    time = models.DateTimeField(default=timezone.now, db_index=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, db_index=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='queued')

    valid_lookups = models.IntegerField(blank=True, null=True, default=None)
    invalid_lookups = models.JSONField(blank=True, null=True, default=None)

    error_info = models.TextField(null=True, blank=True)


    def __str__(self):
        self.user: User
        return f"[{self.user.username}] {self.time} {self.status}"

    class Meta:
        """
        Django meta class
        """
        ordering = ["-time"]

class AddressResult(models.Model):
    """
    Results of the lookup
    """

    IP_TYPES = (
        ("4", 'IPv4'),
        ("6", 'IPv6'),
    )

    uuid = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4)
    lookup = models.ForeignKey(LookupRequest, \
        on_delete=models.PROTECT, related_name='results')

    # Lookup Validity
    valid_from = models.DateTimeField("Lookup Time", default=timezone.now, db_index=True)
    valid_until = models.DateTimeField("Lookup Validity Expires", \
        default=None, blank=True, null=True, db_index=True)

    # IP Data
    ip_address = models.GenericIPAddressField('IP Address', blank=True, null=True, db_index=True)
    ip_version = models.CharField('IP Version',\
         max_length=255, choices=IP_TYPES, db_index=True, blank=True, null=True)

    ### ASN FIELDS ###
    autonomous_system_organization = models.CharField(max_length=255, \
        db_index=True, blank=True, null=True)
    autonomous_system_number = models.IntegerField(db_index=True, blank=True, null=True)

    ### GEO FIELDS ###
    # Postal / ZIP Code
    postal_code = models.CharField("Postal Code", max_length=255, db_index=True, blank=True, null=True)
    postal_confidence = models.IntegerField("Postal Code Confidence", \
        default=0, blank=True, null=True)

    ## Demagraphics
    average_income = models.IntegerField("Location Average Income", blank=True, null=True)
    accuracy_radius = models.IntegerField("Accuracy Radius", blank=True, null=True)
    latitude = models.FloatField("Latitude", blank=True, null=True)
    longitude = models.FloatField("Longitude", blank=True, null=True)
    population_density = models.IntegerField("Population Density", blank=True, null=True)
    timezone = models.CharField("Timezone", max_length=255, blank=True, null=True)


    # City
    city_name = models.CharField("City", max_length=255, db_index=True, blank=True, null=True)
    city_confidence = models.IntegerField("City Confidence", default=0, blank=True, null=True)

    # https://developers.google.com/google-ads/api/data/geotargets#dma
    metro_code = models.IntegerField("Metro Code", db_index=True, blank=True, null=True)

    # State / Region
    region_name = models.CharField("State / Region", \
        max_length=255, db_index=True, blank=True, null=True)
    region_flag = models.CharField("Region Flag", max_length=255, blank=True, null=True)
    region_code = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    region_confidence = models.IntegerField("Region Confidence",default=0, blank=True, null=True)

    # Country
    country_name = models.CharField("Country", max_length=25, db_index=True, blank=True, null=True)
    country_flag = models.CharField("Country", max_length=25, blank=True, null=True)
    country_european_union = models.BooleanField("European Union", default=False, db_index=True)
    country_code = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    country_confidence = models.IntegerField("Country Confidence", default=0, blank=True, null=True)

    # Continent
    continent_name = models.CharField(max_length=255, blank=True, null=True)
    continent_code = models.CharField(max_length=255, blank=True, null=True)

    matches_lists = models.ManyToManyField(ListGenerator)

    bogon = models.CharField(max_length=255, blank=True, null=True)


    def __str__(self):
        flag = ""
        if self.country_flag: 
            flag = f"{self.country_flag} "
        return f"{flag}{self.ip_address} - {self.valid_from}"

    @property
    def ip_object(self) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
        """
        Returns the current object as an ipaddress.IPv4Address | ipaddress.IPv6Address
        """
        return ipaddress.ip_address(str(self.ip_address))

    @property
    def _bogon(self) -> bool:
        """
        Checks if the IP is bogon
        """
        if self.ip_object.is_private:
            return 'Private'
        if self.ip_object.is_multicast:
            return 'Multicast'
        if self.ip_object.is_loopback:
            return 'Loopback'
        if self.ip_object.is_link_local:
            return 'Link Local'
        if self.ip_object.is_reserved:
            return 'Reserved'
        return "No"

    @property
    def valid(self) -> bool:
        """
        Check if the geo data is still valid
        """
        return self.valid_until > timezone.now()

    def _set_lookup_validity(
        self,
        expires_in: datetime.timedelta = None,
        weekly_expiration_day: int = TUESDAY
    ) -> None:
        now = timezone.now()
        self.valid_from = now

        if not expires_in:
            self.valid_until = next_weekday(now, weekly_expiration_day)
        else:
            self.valid_until = now + expires_in

    def __validate__(self):
        """
        Validates IP
        """
        self.ip_version = self.ip_object.version
        self.bogon = self._bogon
        self._set_lookup_validity()
        self.save()

    class Meta:
        """
        Django meta class
        """
        ordering = ["-valid_from"]

# pylint: disable=unused-argument
@receiver(signals.post_save, sender=AddressResult)
def _validate_ip(sender, instance: AddressResult, created: bool, **kwargs):
    """
    Validates the IP version and assigns it to the model
    """
    if created:
        signals.post_save.disconnect(_validate_ip, sender=AddressResult)
        instance.__validate__()
        signals.post_save.connect(_validate_ip, sender=AddressResult)

@receiver(models.signals.post_save, sender=GeoSync)
def _update_geo_expires(sender, instance:GeoSync, *args, **kwargs):
    """
    Geo Yeet
    """
    instance.expires = instance._expires
    signals.post_save.disconnect(_update_geo_expires, sender=GeoSync)
    instance.save()
    signals.post_save.connect(_update_geo_expires, sender=GeoSync)

@receiver(models.signals.post_delete, sender=GeoSync)
def yeet_geo_file(sender, instance:GeoSync, *args, **kwargs):
    """
    Geo Yeet
    """
    instance.yeet()

# pylint: disable=unused-argument
@receiver(signals.post_save, sender=TaskResult)
def _update_task(sender, instance: TaskResult, created: bool, **kwargs):
    """
    Calls a geo update on object save... this allows /admin creation
    """
    try:
        geo_i = GeoSync.objects.get(celery_task_uuid=instance.task_id)
        geo_i.celery_task = instance
        geo_i.save()
    except GeoSync.DoesNotExist:
        pass

# pylint: disable=unused-argument
@receiver(signals.post_save, sender=AccessPlan)
def _create_client(sender, instance: AccessPlan, created: bool, **kwargs):
    """
    Calls a geo update on object save... this allows /admin creation
    """
    if not instance.client:
        new_client = Client.objects.create(
            name=str(instance.uuid),
            throttle_rate=instance.throttle_rate
        )
        new_client.save()
        instance.client = new_client
        signals.post_save.disconnect(_create_client, sender=AccessPlan)
        instance.save()
        signals.post_save.connect(_create_client, sender=AccessPlan)
