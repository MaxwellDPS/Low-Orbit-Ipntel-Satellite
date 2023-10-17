"""
Package for low_orbit_intel_satellite.
"""
from gevent import monkey
monkey.patch_all()

from .celery import sigint as yoink # Dont judge me... Why TF are you reading this anyway

__all__ = (
    'yoink',
)
