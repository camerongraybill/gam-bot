from os import getenv
from typing import Sequence, Tuple, Optional

from pkg_resources import get_distribution

DISCORD_KEY = getenv("DISCORD_KEY", None)

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
    (None, "version", (f"Gam bot version v{get_distribution('gam_bot').version}",)),
)

TRIGGER = "!"

ADD_SOCIAL_SCORE = "⬆️"
REMOVE_SOCIAL_SCORE = "⬇️"
