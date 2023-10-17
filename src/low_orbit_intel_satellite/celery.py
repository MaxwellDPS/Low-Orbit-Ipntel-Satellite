from __future__ import absolute_import, unicode_literals

import os
from celery import Celery

from django.apps import apps

import sigint # pylint: disable = unused-import

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'low_orbit_intel_satellite.settings')

app = Celery('low_orbit_intel_satellite')
app.conf.beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"
app.config_from_object('django.conf:settings', namespace="CELERY")
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])
