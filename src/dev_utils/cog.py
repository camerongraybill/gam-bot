from discord.ext import commands
from discord.ext.commands import Context, Bot

from discord_bot.cog import BaseCog
from discord_bot.models import DiscordUser
from importlib.metadata import version


class DevUtilsCog(BaseCog):
    @commands.command(help="Subscribe to getting a DM when the bot starts up")
    async def subscribe_to_deploy(self, ctx: Context[Bot]) -> None:
        user, _ = await DiscordUser.objects.aget_or_create(
            discord_id=ctx.message.author.id
        )
        user.notify_on_startup = True
        await user.asave()

    @commands.command(help="Unsubscribe from getting a DM when the bot starts up")
    async def unsubscribe_to_deploy(self, ctx: Context[Bot]) -> None:
        user, _ = await DiscordUser.objects.aget_or_create(
            discord_id=ctx.message.author.id
        )
        user.notify_on_startup = False
        await user.asave()

    @commands.command(help="Link to source repository")
    async def source(self, ctx: Context[Bot]) -> None:
        await ctx.message.channel.send(
            "My source can be found at: https://github.com/camerongraybill/gam-bot"
        )

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        users_to_notify = DiscordUser.objects.filter(notify_on_startup=True)
        async for user in users_to_notify:
            discord_user = await self.bot.fetch_user(user.discord_id)
            dm = discord_user.dm_channel or await discord_user.create_dm()
            await dm.send(f"The bot has started up with version {version('gam_bot')}")
