from os import getenv
from typing import Sequence, Optional

from pkg_resources import get_distribution

DISCORD_KEY = getenv("DISCORD_KEY", None)

EASY_MESSAGES: Sequence[tuple[str, Optional[set[str]], Sequence[str]]] = (
    (
        "assemble",
        {"heroes-guild", "general"},
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
<<<<<<< HEAD

ADD_SOCIAL_SCORE = "⬆️"
REMOVE_SOCIAL_SCORE = "⬇️"

WAGER_ERROR_REACTION = "❗"
WAGER_NO_MONEY_REACTION = "💸"
WAGER_SUCCESS_REACTION = "✅"
=======
>>>>>>> Add register_score <emoji> <score> command
