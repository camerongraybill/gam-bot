from tortoise.models import Model
from tortoise import fields


class GamUser(Model):
    id = fields.IntField(pk=True)
    discord_id = fields.IntField()
    gam_coins = fields.IntField()

    def __str__(self):
        return f'discord_id={self.discord_id}, gam_coins={self.gam_coins}'