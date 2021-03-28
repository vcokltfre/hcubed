from discord.ext import commands
from discord import Intents, Message, Embed

from time import time
from loguru import logger
from traceback import format_exc

from .help import Help
from .context import Context

from src.utils.database import Database
from src.utils.cache import TimedCache


class Bot(commands.Bot):
    """A subclass of commands.Bot with additional functionality."""

    def __init__(self, *args, **kwargs):
        logger.info("Starting up...")

        self.start_time = time()

        intents = Intents.all()

        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=Help(),
            *args,
            **kwargs
        )

        self.db: Database = Database()

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

        logger.info(f"Cog loading finished. Success: {success}. Failed: {len(exts) - success}.")

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

        await message.reply(embed=Embed(
            title="Restart Complete",
            colour=0x87CEEB,
        ))
