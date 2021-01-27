from .base import *

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
DEBUG = False

ALLOWED_HOSTS = os.environ["VIRTUAL_HOST"].split(",")

SESSION_COOKIE_SECURE = True
