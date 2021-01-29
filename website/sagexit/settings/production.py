from .base import *

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
DEBUG = False

ALLOWED_HOSTS = os.environ["VIRTUAL_HOST"].split(",")

SESSION_COOKIE_SECURE = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": int(os.environ.get("POSTGRES_PORT", 5432)),
        "NAME": os.environ.get("POSTGRES_NAME"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(asctime)s %(name)s %(levelname)s %(message)s"},
        "brief": {"format": "%(name)s %(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "brief",
        },
        "file": {
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": "/sagexit/log/django.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}

STATIC_ROOT = "/sagexit/static/"
STATIC_URL = "/static/"

MEDIA_ROOT = "/sagexit/media/"
MEDIA_URL = "/media/"
