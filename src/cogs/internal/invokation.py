from discord import Message
from discord.ext import commands

from copy import copy
from re import compile
from loguru import logger

from src.internal.bot import Bot
from src.internal.context import Context


INLINE = compile(r"{i:[^}]+}")
ISUM = compile(r"{s:[^}]+}")


class Invokation(commands.Cog):
    """Invoke commands from within messages."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        prefix = await self.bot.get_prefix(message)

        if message.content.startswith(prefix):
            return

        if match := INLINE.search(message.content):
            command = match.group()[3:-1]
        elif match := ISUM.search(message.content):
            command = "jsk py " + match.group()[3:-1]
        else:
            return

        msg = copy(message)
        msg.content = prefix + command

        await self.bot.process_commands(msg)


def setup(bot: Bot):
    bot.add_cog(Invokation(bot))
