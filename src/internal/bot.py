import asyncio
from time import time
from traceback import format_exc

from aiohttp import ClientSession
from discord import AllowedMentions, Embed, Intents, Message
from discord.ext import commands
from git import Repo
from loguru import logger

from src.utils.cache import TimedCache
from src.utils.database import Database

from .context import Context
from .help import Help


class Bot(commands.AutoShardedBot):
    """A subclass of commands.AutoShardedBot with additional functionality."""

    def __init__(self, *args, **kwargs):
        logger.info("Starting up...")

        self.start_time = time()

        intents = Intents.all()

        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=Help(),
            allowed_mentions=AllowedMentions(
                roles=False,
                everyone=False,
                replied_user=False,
            ),
            *args,
            **kwargs,
        )

        self.db: Database = Database()
        self.http_session: ClientSession = None

        self.prefixes = TimedCache(30)

    def load_extensions(self, *exts) -> None:
        """Load a given set of extensions."""

        logger.info(f"Starting loading {len(exts)} cogs...")

        success = 0

        for ext in exts:
            try:
                self.load_extension(ext)
            except:
                logger.error(f"Error while loading {ext}:\n{format_exc()}")
            else:
                logger.info(f"Successfully loaded cog {ext}.")
                success += 1

        logger.info(
            f"Cog loading finished. Success: {success}. Failed: {len(exts) - success}."
        )

    async def maybe_delete(self, invoker: Message, message: Message) -> None:
        await message.add_reaction("❌")

        check = (
            lambda r, u: u == invoker.author
            and str(r.emoji) == "❌"
            and r.message.id == message.id
        )

        try:
            reaction, user = await self.wait_for(
                "reaction_add", check=check, timeout=30
            )
        except asyncio.TimeoutError:
            await message.clear_reaction("❌")
            return

        await message.delete()

    async def login(self, *args, **kwargs) -> None:
        """Create the database connection before login."""
        logger.info("Logging in to Discord...")

        await self.db.setup()

        await super().login(*args, **kwargs)

    async def get_prefix(self, message: Message):
        """Get a dynamic prefix."""

        if message.content.startswith("hc!") or not message.guild:
            return "hc!"

        prefix = self.prefixes[message.guild.id]

        if prefix:
            return prefix

        guild = await self.db.fetch_guild(message.guild.id, message.guild.owner_id)
        self.prefixes[message.guild.id] = guild["prefix"]

        return self.prefixes[message.guild.id]

    async def get_context(self, message: Message):
        """Get the context with the custom context class."""

        return await super().get_context(message, cls=Context)

    async def on_connect(self):
        """Log the connect event."""

        self.http_session = ClientSession()

        logger.info("Connected to Discord.")

    async def on_ready(self):
        restart = await self.db.get_restart()

        if not restart:
            return

        channel = self.get_channel(restart["cid"])
        if not channel:
            return

        message = await channel.fetch_message(restart["mid"])
        if not message:
            return

        await message.reply(
            embed=Embed(
                title="Restart Complete",
                colour=0x87CEEB,
            )
        )

        alerts = await self.db.get_restart_alerts()
        repo = Repo(".")

        embed = Embed(
            title="Restart Completed",
            colour=0x87CEEB,
            description=f"Commit hash: [{str(repo.head.commit)[:7]}](https://github.com/vcokltfre/hcubed/commit/{repo.head.commit})",
        )

        for alert in alerts:
            channel = self.get_channel(alert["channelid"])
            self.loop.create_task(channel.send(embed=embed))
