from os import getenv
from typing import Sequence, Optional

from pkg_resources import get_distribution


EASY_MESSAGES: Sequence[tuple[str, Optional[set[str]], Sequence[str]]] = (
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
    (
        "turkey_thank",
        None,
        ("https://camerongraybill.dev/turkey_thank.png",),
    )
    (
        "doubt",
        None,
        ("https://camerongraybill.dev/doubt.jpg",),
    ),
    ("version", None, (f"Gam bot version {get_distribution('gam_bot').version}",)),
)

# Discord settings

DISCORD_COGS = [
    "lmgtfy.cog.LMGTFYCog",
    "easy_messages.cog.EasyCog",
    "social_score.cog.SocialScoreCog",
    "gam_coins.cog.GamCoinsCog",
    "discord_bot.cog.UserTrackingCog",
    "dev_utils.cog.DevUtilsCog",
]

DISCORD_KEY = getenv("DISCORD_KEY", None)

DISCORD_COMMAND_PREFIX = getenv("DISCORD_COMMAND_PREFIX", "!")
