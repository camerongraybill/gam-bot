from ._django import *  # noqa: F403
from ._gam import *  # noqa: F403

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-aljvt0!4(872mjb&$1z4f1p8)ahu^(6y4^vi)y9drjlsu)@^1p"  # nosec

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # nosec
