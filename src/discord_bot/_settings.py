from functools import cached_property
from importlib import import_module
from typing import Optional, Collection, Type, cast

from django.conf import settings as django_settings

from discord_bot.cog import BaseCog


def _split_cog_path(cog_path: str) -> tuple[str, str]:
    sp = cog_path.split(".")
    return ".".join(sp[:-1]), sp[-1]


class _Settings:
    @cached_property
    def COGS(self) -> Collection[Type[BaseCog]]:
        cog_path: str
        all_cogs = []
        # Path should be path.to.module.CogClassName
        for cog_path in getattr(django_settings, "DISCORD_COGS", []):
            module_path, cog_name = _split_cog_path(cog_path)
            try:
                module = import_module(module_path)
            except ModuleNotFoundError:
                raise Exception(
                    f"Attempted to import module {module_path} from DISCORD_MODULES, but it does not exist."
                )
            if not hasattr(module, cog_name):
                raise Exception(
                    f"Attempted to import cog named {cog_name} from module {module_path} but {module_path} has no attribute {cog_name}"
                )

            cls = getattr(module, cog_name)
            if not issubclass(cls, BaseCog):
                raise Exception(
                    f"Attempted to set up cog {cog_path} but it is not a subclass of discord_bot.BaseCog"
                )

            all_cogs.append(cls)
        return tuple(set(all_cogs))

    @cached_property
    def KEY(self) -> Optional[str]:
        return cast(Optional[str], getattr(django_settings, "DISCORD_KEY", None))

    @cached_property
    def COMMAND_PREFIX(self) -> str:
        return cast(str, getattr(django_settings, "DISCORD_COMMAND_PREFIX", "!"))


def get_settings() -> _Settings:
    return _Settings()
