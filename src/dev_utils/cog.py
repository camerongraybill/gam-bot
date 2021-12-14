from discord.ext import commands
from discord.ext.commands import Context

from discord_bot.cog import BaseCog
from discord_bot.models import DiscordUser

from pkg_resources import get_distribution


# pylint: disable=no-self-use
class DevUtilsCog(BaseCog):
    @commands.command(help="Subscribe to getting a DM when the bot starts up")
    async def subscribe_to_deploy(self, ctx: Context) -> None:
        user, _ = await DiscordUser.async_qs().async_get_or_create(
            discord_id=ctx.message.author.id
        )
        user.notify_on_startup = True
        await user.async_save()

    @commands.command(help="Unsubscribe from getting a DM when the bot starts up")
    async def unsubscribe_to_deploy(self, ctx: Context) -> None:
        user, _ = await DiscordUser.async_qs().async_get_or_create(
            discord_id=ctx.message.author.id
        )
        user.notify_on_startup = False
        await user.async_save()

    @commands.command(help="Link to source repository")
    async def source(self, ctx: Context) -> None:
        await ctx.message.channel.send(
            "My source can be found at: https://github.com/camerongraybill/gam-bot"
        )

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        users_to_notify = (
            await DiscordUser.async_qs().filter(notify_on_startup=True).to_list()
        )
        for user in users_to_notify:
            discord_user = await self.bot.fetch_user(user.discord_id)
            dm = discord_user.dm_channel or await discord_user.create_dm()
            await dm.send(
                f"The bot has started up with version {get_distribution('gam_bot').version}"
            )
