from functools import cached_property
from typing import cast

from django.conf import settings as django_settings


class _Settings:
    @cached_property
    def SUBSCRIBED_CHANNEL(self) -> str:
        return cast(
            str, getattr(django_settings, "AOC_SUBSCRIBED_CHANNEL", "bot-commands")
        )


def get_settings() -> _Settings:
    return _Settings()
