import os

from core.settings.base import *  # noqa

from core.settings.base import INSTALLED_APPS, MIDDLEWARE


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
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3", # noqa
        }
    }


ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    os.environ["NGROK_HOST"]
]
