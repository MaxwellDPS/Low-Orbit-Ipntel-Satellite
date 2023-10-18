"""
 ___________________ 
< SET ALL THE THINGZ >
 ------------------- 
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
"""
import hashlib
import os
import logging

from datetime import timedelta
from pathlib import Path
import socket
import uuid
import django.core.files.storage
import low_orbit_intel_satellite.storage_backends

from kombu import Queue
# from rest_framework.settings import api_settings

######################################################################
# 🌶️ SPICY WARNING ‼️
# SENTRY TELEMETRY
SENTRY_SEND_TELEMETRY = os.getenv("SENTRY_SEND_TELEMETRY", "False").lower() in ("true", "1", "t")
######################################################################

if SENTRY_SEND_TELEMETRY:
    import sentry_sdk

    SENTRY_DSN = os.getenv("SENTRY_DSN")
    if not SENTRY_DSN:
        raise ValueError("Must set SENTRY_DSN if using SENTRY_SEND_TELEMETRY")

    SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "1.0"))

    sentry_sdk.init(
        SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=SENTRY_SAMPLE_RATE,
    )


#Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = os.getenv('SECRET_KEY', hashlib.blake2b(uuid.uuid5(uuid.NAMESPACE_DNS, socket.gethostname()).bytes).hexdigest())

SHITS_VALID_YO = ['t', '1', 'yeet', 'true', 'yee', 'yes', 'duh', 'yesdaddy', 'ok']

# SECURITY WARNING: don't run with debug turned on in production!
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

if os.getenv("FORCE_SECURE", "False").lower() in ("true", "1", "t"):
    # Honor the 'X-Forwarded-Proto' header for request.is_secure()
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',')
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000000
DJANGO_WEB_MAX_REQUESTS = 3000
DJANGO_WEB_TIMEOUT = 15

# Application references
# https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'corsheaders',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'durin',
    'django_celery_results',
    'django_celery_beat',
    'drf_yasg',
    "storages",
    'sigint',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend'
]

# Middleware framework
# https://docs.djangoproject.com/en/2.1/topics/http/middleware/
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
]

ROOT_URLCONF = 'low_orbit_intel_satellite.urls'

# Template configuration
# https://docs.djangoproject.com/en/2.1/topics/templates/
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
#                'reactor.context_processors.side_bar',
            ],
        },
    },
]

WSGI_APPLICATION = 'low_orbit_intel_satellite.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
     'default': {
        'ENGINE': 'django_db_geventpool.backends.postgresql_psycopg2',
        'NAME': os.getenv('SQL_DATABASE'),
        'USER': os.getenv('SQL_USER'),
        'PASSWORD': os.getenv('SQL_PASSWORD'),
        'HOST': os.getenv('SQL_HOST', '127.0.0.1'),
        'PORT': os.getenv('SQL_PORT', '5432'),
        'ATOMIC_REQUESTS': False,
        'CONN_MAX_AGE': 0,
        'OPTIONS': {
            'MAX_CONNS': 20,
            'REUSE_CONNS': 10
        }
     }
 }

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_L10N = True
USE_TZ = True


SESSION_EXPIRE_SECONDS = int(os.getenv('SESSION_EXPIRE_SECONDS', '3600'))
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD = 60 # group by minute


DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

###########################################################
# LOGGING STUFFZ
###########################################################

# Logging Configuration
# Get loglevel from env
LOGLEVEL = os.getenv('DJANGO_LOGLEVEL', 'info').upper()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOGLEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": LOGLEVEL,
            "propagate": False,
        },
    },
}


########################################################################
# Celery Stuffz
########################################################################
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# CELERY_BROKER_HEARTBEAT = 0
# BROKER_HEARTBEAT = 0
# CELERY_BROKER_HEARTBEAT_CHECKRATE = 0.5
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND',"django-db")
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Chicago'
CELERY_PREFETCH_MULTIPLIER = 1
CELERY_IMPORTS = ('sigint.tasks',)
CELERY_RESULT_EXTENDED = True

# CELERY_ALWAYS_EAGER = True
CELERY_TASK_RESULT_EXPIRES = 120  # 1 mins
CELERYD_MAX_TASKS_PER_CHILD = 1500
CELERYD_PREFETCH_MULTIPLIER = 1
CELERY_ACKS_LATE = False
CELERY_CREATE_MISSING_QUEUES = True
CELERY_TASK_DEFAULT_QUEUE = "sync"
CELERY_QUEUES = (
    Queue(
        'sync'
    )
)

CELERY_TASK_ROUTES  = {
    'skynnet.tasks.*': {'queue': 'sync'}
}

###########################################################################################
# Rest API STUFFz
###########################################################################################
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_PERMISSION_CLASSES': (
      'rest_framework.permissions.IsAuthenticated',
    ),
    "DEFAULT_THROTTLE_RATES": {"user_per_client": "120/min"},
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'durin.auth.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication', 
    )

}

DEFAULT_TOKEN_TTL = int(os.getenv("DEFAULT_TOKEN_TTL", "30"))


REST_DURIN = {
        "DEFAULT_TOKEN_TTL": timedelta(minutes=DEFAULT_TOKEN_TTL),
        "TOKEN_CHARACTER_LENGTH": 64,
        "USER_SERIALIZER": None,
        "AUTH_HEADER_PREFIX": "Token",
#        "EXPIRY_DATETIME_FORMAT": api_settings.DATETIME_FORMAT,
        "TOKEN_CACHE_TIMEOUT": 60,
        "REFRESH_TOKEN_ON_LOGIN": False,
        "AUTHTOKEN_SELECT_RELATED_LIST": ["user"],
        "API_ACCESS_CLIENT_NAME": None,
        "API_ACCESS_EXCLUDE_FROM_SESSIONS": False,
        "API_ACCESS_RESPONSE_INCLUDE_TOKEN": False,
}

CORS_ALLOWED_HOSTS="http://127.0.0.1:8080 https://127.0.0.1:8443 http://127.0.0.1 https://127.0.0.1 http://localhost:8080 https://localhost:8443 http://localhost https://localhost"
# Enable CORS for all domains
if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True
    CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_HOSTS",  CORS_ALLOWED_HOSTS).split(" ")
else:
    CORS_ORIGIN_ALLOW_ALL = os.getenv("CORS_ORIGIN_ALLOW_ALL", "False").lower() in SHITS_VALID_YO
    CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_HOSTS", CORS_ALLOWED_HOSTS).split(" ")

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
CORS_ALLOW_CREDENTIALS = True
SESSION_COOKIE_SAMESITE = None
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = True
CSRF_HEADER_NAME="HTTP_CSRFTOKEN"

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    }
}


###########################################################
# S3 JAZZ 🪣
###########################################################
AWS_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "")
AWS_DEFAULT_ACL = None
AWS_S3_CUSTOM_DOMAIN = f"{AWS_S3_ENDPOINT_URL.replace('https://','')}"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

###########################################################
# STATIC FILE STUFFZ
# (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
###########################################################
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_USE_S3 = os.getenv("STATIC_USE_S3", "False").lower() in SHITS_VALID_YO
STATICFILES_DIRS = (os.path.join(BASE_DIR, "staticfiles"),)

if STATIC_USE_S3:
     # STORE A FILE 🗂️
    STATIC_LOCATION = "static"
    STATIC_URL = (
        f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STORAGE_BUCKET_NAME}/{STATIC_LOCATION}/"
    )
    STATICFILES_STORAGE = "low_orbit_intel_satellite.storage_backends.StaticStorage"
else:
    STATIC_URL = "/static/"
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

###########################################################
# GEO STUFFZ
###########################################################
MAX_MIND_KEY = os.getenv("MAX_MIND_KEY")
GEOIP_USE_S3 = os.getenv("GEOIP_USE_S3", "False").lower() in SHITS_VALID_YO
IP_GEO_LOOKUP_TTL: timedelta = timedelta(days=int(os.getenv("IP_GEO_LOOKUP_TTL", "1")))

GEOIP_PATH = Path(os.getenv("GEO_PATH", os.path.join(BASE_DIR, 'geofiles')))
GEOIP_PATH.mkdir(exist_ok=True)
MEDIA_ROOT = GEOIP_PATH
GEOIP_STORAGE = django.core.files.storage.FileSystemStorage

if STATIC_USE_S3:
    # STORE A FILE 🗂️
    DEFAULT_FILE_STORAGE = low_orbit_intel_satellite.storage_backends.PrivateMediaStorage
    GEOIP_LOCATION = "geoip"
    GEOIP_URL = (
        f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STORAGE_BUCKET_NAME}/{GEOIP_LOCATION}/"
    )
    GEOIP_STORAGE = low_orbit_intel_satellite.storage_backends.GeoIPMediaStorage
    GEOIP_PATH = None

GEOIP_CITY = "city/GeoLite2-City.mmdb"
GEOIP_COUNTRY = "country/GeoLite2-Country.mmdb"
GEOIP_ASN = "asn/GeoLite2-ASN.mmdb"


###########################################################
# PRUNE STUFFZ
###########################################################
IP_GEO_CACHE_PRUNE_DAYS: timedelta = timedelta(days=int(os.getenv("IP_GEO_CACHE_PRUNE_DAYS", "90")))
GEO_SYNC_PRUNE_DAYS: timedelta = timedelta(days=int(os.getenv("GEO_SYNC_PRUNE_DAYS", "30")))
GEO_SYNC_PRUNE_FILES: bool = os.getenv("GEO_SYNC_PRUNE_FILES", "true") in SHITS_VALID_YO
USER_LOOKUP_PRUNE_DAYS: timedelta = timedelta(days=int(os.getenv("USER_LOOKUP_PRUNE_DAYS", "30")))
GEO_SYNC_ADMIN_GROUP = 'geo-sync-admins'
GEO_SYNC_USERAGENT = "low_orbit_intel_satellite/api v0.69"


# YOU THINK YOU DID SOMETHING STUPID... Youre proably right 🫰👉
try:
    LOCAL_SETTINGS
except NameError:
    try:
        from low_orbit_intel_satellite.settings_local import *
    except ImportError:
        pass
