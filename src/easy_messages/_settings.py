from functools import cached_property
from typing import Optional, Collection, Sequence, cast

from django.conf import settings as django_settings

CommandConfig = tuple[str, Optional[set[str]], Sequence[str]]


# pylint: disable=too-few-public-methods
class _Settings:
    @cached_property
    def COMMANDS(self) -> Collection[CommandConfig]:
        return cast(
            Collection[CommandConfig], getattr(django_settings, "EASY_MESSAGES", [])
        )


def get_settings() -> _Settings:
    return _Settings()
