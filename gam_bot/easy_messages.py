from typing import Sequence, Optional
from gam_bot.settings import EASY_MESSAGES


def easy_message_processor(
    content: str, channel: Optional[str]
) -> Optional[Sequence[str]]:
    for channels, keyword, response in EASY_MESSAGES:
        channel_matches = channels is None or channel in channels
        content_matches = content == keyword
        if channel_matches and content_matches:
            return response
    return None
