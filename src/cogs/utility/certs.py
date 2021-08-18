from re import Pattern
from re import compile as re_compile
from time import time

from aiocertstream import Client
from discord import File
from discord.ext import commands

from src.internal.bot import Bot
from src.internal.context import Context


class CertContext:
    def __init__(
        self, cog: commands.Cog, expire_after: int, pattern: Pattern, callback
    ) -> None:
        self.cog = cog
        self.expire_after = expire_after
        self.pattern = pattern
        self.callback = callback

        self._client = Client()

        self._client.listen(self.handle)

    def kill(self) -> None:
        self.cog.bot.loop.create_task(self._client._ws.close())

    async def start(self) -> None:
        self.cog.bot.loop.call_later(self.expire_after, self.kill)

        await self._client.start()

    async def handle(self, data: dict) -> None:
        domains = data["data"]["leaf_cert"]["all_domains"]
        for domain in domains:
            if self.pattern.match(domain):
                await self.callback(f"Found domain: {domain}")


class Certs(commands.Cog):
    """Listen for specific ceritificate updates."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(name="certs")
    @commands.is_owner()
    async def certs(self, ctx: Context, dur: int, *, pattern: str = None) -> None:
        """Listen for specific ceritificate updates."""

        msg = await ctx.reply(
            f"Starting scan on pattern `{pattern}` for {dur} seconds."
        )

        thread = await ctx.create_message_thread(name="Certificate Scanning", auto_archive_duration=60)

        context = CertContext(self, dur, re_compile(pattern), thread.send)

        await context.start()
        await context._client._session.close()
        del context

        await msg.reply("Done.")


def setup(bot: Bot):
    bot.add_cog(Certs(bot))
