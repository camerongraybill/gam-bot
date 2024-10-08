from importlib.metadata import version
from os import getenv
from typing import Sequence, Optional


EASY_MESSAGES: Sequence[tuple[str, Optional[set[str]], Sequence[str]]] = (
    (
        "assemble",
        {"recruiting-board", "heroes-guild"},
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
    ),
    (
        "doubt",
        None,
        ("https://camerongraybill.dev/doubt.jpg",),
    ),
    ("version", None, (f"Gam bot version {version('gam_bot')}",)),
    (
        "assemble2",
        None,
        (
            "<@&789269532875292683> Assemble!",
            "https://camerongraybill.dev/losers.png",
        ),
    ),
)

# Discord settings

DISCORD_COGS = [
    "lmgtfy.cog.LMGTFYCog",
    "social_score.cog.SocialScoreCog",
    "gam_coins.cog.GamCoinsCog",
    "discord_bot.cog.UserTrackingCog",
    "dev_utils.cog.DevUtilsCog",
    "advent_of_code.cog.AdventOfCodeCog",
    "remind_me.cog.RemindMeCog",
]

DISCORD_KEY = getenv("DISCORD_KEY", None)

DISCORD_COMMAND_PREFIX = getenv("DISCORD_COMMAND_PREFIX", "!")

AOC_SUBSCRIBED_CHANNEL = "cooking-guild"
