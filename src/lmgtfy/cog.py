from discord.ext import commands
from discord.ext.commands import Context, Bot

from discord_bot.cog import BaseCog
from yarl import URL


class LMGTFYCog(BaseCog):
    @commands.command(
        help="Creates a LMGTFY link for the last message sent or the message you reply to",
        pass_context=True,
    )
    async def lmgtfy(self, ctx: Context[Bot]) -> None:
        message = ctx.message
        chan = message.channel
        if message.reference is not None and message.reference.message_id is not None:
            # use message being replied to
            original = await chan.fetch_message(message.reference.message_id)
        else:
            # use message immediately before this one
            original = await anext(
                chan.history(limit=1, before=message, oldest_first=False)
            )

        await original.reply(
            str(URL("https://lmgtfy.app/").with_query({"q": original.content}))
        )
