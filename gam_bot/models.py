from tortoise.models import Model
from tortoise import fields


class GamUser(Model):
    discord_id = fields.IntField(pk=True)
    gam_coins = fields.IntField(default=0)

    def __str__(self):
        return f'discord_id={self.discord_id}, gam_coins={self.gam_coins}'