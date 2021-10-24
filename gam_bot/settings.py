from os import environ
from typing import Sequence, Tuple, Optional
from pkg_resources import get_distribution

DISCORD_KEY = environ.get("DISCORD_KEY", None)

EASY_MESSAGES: Sequence[Tuple[Optional[Sequence[str]], str, Sequence[str]]] = (
    (
        ("heroes-guild",),
        "assemble",
        (
            "<@&471829212626681866> Assemble!",
            "https://www.camerongraybill.dev/assemble.jpg",
        ),
    ),
    (
        ("heroes-guild",),
        "thank",
        ("https://camerongraybill.dev/thank-you-for-your-service.jpg",),
    ),
    (None, "version", (f"Gam bot version {get_distribution('gam_bot').version}",)),
)

TRIGGER = "!"

PORT = int(environ.get("PORT", 8081))
HOST = "0.0.0.0"  # nosec

DB_CONN_STR = environ.get("DB_CONN_STR", "sqlite://db.sqlite3")

TORTOISE_ORM = {
    "connections": {"default": DB_CONN_STR},
    "apps": {"models": {"models": ["gam_bot.models", "aerich.models"]}},
}
