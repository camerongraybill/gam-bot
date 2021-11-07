from functools import cached_property
from typing import cast

from django.conf import settings as django_settings


class _Settings:
    @cached_property
    def NO_MONEY_REACTION(self) -> str:
        return cast(str, getattr(django_settings, "GAM_COINS_NO_MONEY_REACTION", "💸"))

    @cached_property
    def ERROR_REACTION(self) -> str:
        return cast(str, getattr(django_settings, "GAM_COINS_ERROR_REACTION", "❗"))

    @cached_property
    def SUCCESS_REACTION(self) -> str:
        return cast(str, getattr(django_settings, "GAM_COINS_SUCCESS_REACTION", "✅"))

    @cached_property
    def INCOME_PER_MINUTE(self) -> int:
        return cast(int, getattr(django_settings, "GAM_COINS_INCOME_PER_MINUTE", 10))

    @cached_property
    def ALL_IN_REACTION(self) -> str:
        return cast(str, getattr(django_settings, "GAM_COINS_ALL_IN_REACTION", "🤑"))


def get_settings() -> _Settings:
    return _Settings()
