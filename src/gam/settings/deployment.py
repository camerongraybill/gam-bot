# pylint: disable=unused-wildcard-import, wildcard-import

from ._django import *
from ._gam import *

from os import environ

DEBUG = environ.get("DEBUG", "false").lower() == "true"

STATIC_ROOT = environ.get("STATIC_ROOT")

SECRET_KEY = environ["SECRET_KEY"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": environ["DB_NAME"],
        "USER": environ["DB_USER"],
        "PASSWORD": environ["DB_PASSWORD"],
        "HOST": environ["DB_HOST"],
        "PORT": int(environ["DB_PORT"]),
    }
}

ALLOWED_HOSTS = [environ["ALLOWED_HOST"]]
