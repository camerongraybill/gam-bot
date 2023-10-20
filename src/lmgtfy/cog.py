from urllib.parse import urlencode

from discord.ext import commands
from discord.ext.commands import Context

from discord_bot.cog import BaseCog


class LMGTFYCog(BaseCog):
    @commands.command(
        help="Creates a LMGTFY link for the last message sent or the message you reply to"
    )
    async def lmgtfy(self, ctx: Context) -> None:
        message = ctx.message
        chan = message.channel
        if message.reference is not None and message.reference.message_id is not None:
            # use message being replied to
            original = await chan.fetch_message(id=message.reference.message_id)
        else:
            # use message immediately before this one
            original = await chan.history(
                limit=1, before=message, oldest_first=False
            ).next()

        query = urlencode({"q": original.content})
        await original.reply(f"https://lmgtfy.app/?{query}")
