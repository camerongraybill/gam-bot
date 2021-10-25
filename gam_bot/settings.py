from os import environ
from typing import Sequence, Tuple, Optional
from pkg_resources import get_distribution
from gam_bot.command import REGISTRY, Command

DISCORD_KEY = environ["DISCORD_KEY"]

    #Sequence[Tuple[Optional[Sequence[str]], str, Sequence[str]]] = (
EASY_MESSAGES: Sequence[Command] = (
    REGISTRY.from_args("assemble", {"heroes-guild"},
        (
            "<@&471829212626681866> Assemble!",
            "https://www.camerongraybill.dev/assemble.jpg",
        ),
    ),
    REGISTRY.from_args("thank", {"heroes-guild"},
        ("https://camerongraybill.dev/thank-you-for-your-service.jpg",),
    ),
    REGISTRY.from_args("version", None, (f"Gam bot version {get_distribution('gam_bot').version}",)),
)

for command in EASY_MESSAGES:
    REGISTRY.register(command)

COMMAND_MESSAGE: Sequence[Tuple[Optional]]

TRIGGER = "!"

PORT = int(environ.get("PORT", 8081))
HOST = "0.0.0.0"  # nosec
