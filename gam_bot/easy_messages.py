from typing import Sequence, Optional
from gam_bot.settings import EASY_MESSAGES


def easy_message_processor(
    content: str, channel: Optional[str]
) -> Optional[Sequence[str]]:
    for command in EASY_MESSAGES:
        if command.match(channel, content):
            return command.call(channel, content)
    return None
