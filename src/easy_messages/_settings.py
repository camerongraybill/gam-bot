from functools import cached_property
from typing import Optional, Collection, Sequence

from django.conf import settings as django_settings

CommandConfig = tuple[str, Optional[set[str]], Sequence[str]]


class _Settings:
    @cached_property
    def COMMANDS(self) -> Collection[CommandConfig]:
        return getattr(django_settings, 'EASY_MESSAGES', [])


def get_settings() -> _Settings:
    return _Settings()
