from functools import cached_property

from django.conf import settings as django_settings


class _Settings:
    @cached_property
    def NO_MONEY_REACTION(self) -> str:
        return getattr(django_settings, 'GAM_COINS_NO_MONEY_REACTION', "💸")

    @cached_property
    def ERROR_REACTION(self) -> str:
        return getattr(django_settings, 'GAM_COINS_ERROR_REACTION', "❗")

    @cached_property
    def SUCCESS_REACTION(self) -> str:
        return getattr(django_settings, 'GAM_COINS_SUCCESS_REACTION', "✅")


def get_settings() -> _Settings:
    return _Settings()
