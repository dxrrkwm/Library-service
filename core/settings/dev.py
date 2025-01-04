import os

from dotenv import load_dotenv

from core.settings.base import *
from core.settings.prod import DATABASES

load_dotenv()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "fjsdlfjsdfhdaidhaodaklasdjaslaldnawloijzcxvme"

INSTALLED_APPS.append("debug_toolbar")

MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

INTERNAL_IPS = [
    "localhost",
    "127.0.0.1",
]

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = None
if os.environ.get("IN_DOCKER"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": os.environ["POSTGRES_HOST"],
            "NAME": os.environ["POSTGRES_DB"],
            "USER": os.environ["POSTGRES_USER"],
            "PASSWORD": os.environ["POSTGRES_PASSWORD"],
            "PORT": os.environ["POSTGRES_PORT"]
        }
    }
if DATABASES is None:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3", # noqa
        }
    }
