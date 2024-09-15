from ._django import *  # noqa: F403
from ._gam import *  # noqa: F403

from os import environ

DEBUG = environ.get("DEBUG", "false").lower() == "true"

STATIC_ROOT = environ.get("STATIC_ROOT")

SECRET_KEY = environ["SECRET_KEY"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": environ["DB_NAME"],
        "USER": environ["DB_USER"],
        "PASSWORD": environ["DB_PASSWORD"],
        "HOST": environ["DB_HOST"],
        "PORT": int(environ["DB_PORT"]),
    }
}

ALLOWED_HOSTS = [environ["ALLOWED_HOST"]]
