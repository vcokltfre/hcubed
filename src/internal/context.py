from discord import ChannelType, Message, TextChannel, Thread
from discord.abc import Snowflake
from discord.ext.commands import Context as _BaseContext


class Context(_BaseContext):
    """A Custom Context for extra functionality."""

    async def create_message_thread(
        self, name: str, *, auto_archive_duration: int = 1440
    ) -> Thread:
        self.message: Message
        return await self.message.create_thread(
            name=name, auto_archive_duration=auto_archive_duration
        )

    async def create_channel_thread(
        self,
        name: str,
        *,
        message: Snowflake = None,
        auto_archive_duration: int = 1440,
        private: bool = False,
    ) -> Thread:
        self.channel: TextChannel
        return await self.channel.create_thread(
            name=name,
            message=message,
            auto_archive_duration=auto_archive_duration,
            type=ChannelType.private if private else ChannelType.public,
        )
