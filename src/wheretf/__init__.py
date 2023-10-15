"""
Package for wheretf.
"""
from gevent import monkey
monkey.patch_all()

from .celery import skynet as yoink # Dont judge me... Why TF are you reading this anyway

__all__ = (
    'yoink',
)
