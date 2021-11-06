from django.test import TestCase

from discord_bot.models import DiscordUser
from .models import SocialScore


class TestStuff(TestCase):
    def test_start_with_nothing(self) -> None:
        score = SocialScore.objects.create(
            user=DiscordUser.objects.create(discord_id=1)
        )
        self.assertEqual(score.score, 0)
