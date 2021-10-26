from os import getenv
from typing import Sequence, Optional, Tuple, Set

from pkg_resources import get_distribution

DISCORD_KEY = getenv("DISCORD_KEY", None)

EASY_MESSAGES: Sequence[Tuple[str, Optional[Set[str]], Sequence[str]]] = (
    (
        "assemble",
        {"heroes-guild"},
        (
            "<@&471829212626681866> Assemble!",
            "https://www.camerongraybill.dev/assemble.jpg",
        ),
    ),
    (
        "thank",
        None,
        ("https://camerongraybill.dev/thank-you-for-your-service.jpg",),
    ),
    ("version", None, (f"Gam bot version {get_distribution('gam_bot').version}",)),
)


TRIGGER = "!"

ADD_SOCIAL_SCORE = "⬆️"
REMOVE_SOCIAL_SCORE = "⬇️"
