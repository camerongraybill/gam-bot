from typing import Sequence, Optional
from django.conf import settings


def easy_message_processor(
    content: str, channel: Optional[str]
) -> Optional[Sequence[str]]:
    for channels, keyword, response in settings.EASY_MESSAGES:
        channel_matches = channels is None or channel in channels
        content_matches = content == keyword
        if channel_matches and content_matches:
            return response
    return None
