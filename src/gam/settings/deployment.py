# pylint: disable=unused-wildcard-import, wildcard-import

from ._django import *
from ._gam import *

from os import environ

DEBUG = False

SECRET_KEY = environ["SECRET_KEY"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "gam",
        "USER": "gam",
        "PASSWORD": environ["DB_PASSWORD"],
        "HOST": environ["DB_DB_HOST"],
        "PORT": 5432,
    }
}
