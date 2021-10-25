from django.test import TestCase
from .models import GamUser

# Create your tests here.


class TestUsers(TestCase):
    def test_users_have_no_coins(self) -> None:
        self.assertEqual(GamUser.objects.create().gam_coins, 0)
