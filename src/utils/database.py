from asyncpg import create_pool
from os import getenv, walk
from traceback import format_exc
from datetime import datetime

from loguru import logger


class Database:
    """A database interface for the bot to connect to Postgres."""

    def __init__(self):
        self.guilds = {}

    async def setup(self):
        logger.info("Setting up database...")
        self.pool = await create_pool(
            host=getenv("DB_HOST", "127.0.0.1"),
            port=getenv("DB_PORT", 5432),
            database=getenv("DB_DATABASE"),
            user=getenv("DB_USER", "root"),
            password=getenv("DB_PASS", "password"),
        )
        logger.info("Database setup complete.")

        await self.automigrate()

    async def automigrate(self):
        allow = getenv("AUTOMIGRATE", "false")

        if allow != "true":
            logger.info("Automigrating is disabled, skipping migration attempt.")
            return

        try:
            migration = await self.fetchrow("SELECT id FROM Migrations ORDER BY id DESC LIMIT 1;")
        except Exception as e:
            print(e)
            migration = None

        migration = migration["id"] if migration else 0

        fs = []

        for root, dirs, files in walk("./src/data/"):
            for file in files:
                mnum = int(file[0:4])
                fs.append((mnum, file))

        fs.sort()
        fs = [f for f in fs if f[0] > migration]

        if not fs:
            return

        logger.info("Running automigrate...")

        for file in fs:
            res = await self.run_migration(file[1], file[0])
            if not res:
                break

        logger.info("Finished automigrate.")

    async def run_migration(self, filename: str, num: int):
        logger.info(f"Running migration {filename}...")
        try:
            with open(f"./src/data/{filename}") as f:
                await self.execute(f.read())
            await self.execute("INSERT INTO Migrations VALUES ($1);", num)
        except Exception as e:
            logger.error(f"Failed to run migration {filename}: {format_exc()}")
            return False
        else:
            logger.info(f"Successfully ran migration {filename}.")
            return True

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as conn:
            await conn.execute(query, *args)

    async def fetchrow(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def create_user(self, id: int):
        return await self.fetchrow("INSERT INTO Users (id) VALUES ($1) RETURNING *;", id)

    async def fetch_user(self, id: int):
        user = await self.fetchrow("SELECT * FROM Users WHERE id = $1;", id)

        if not user:
            user = await self.create_user(id)

        return user

    async def create_guild(self, id: int, owner_id: int):
        user = await self.fetch_user(owner_id)

        if user["banned"]:
            raise ValueError("User is banned.")

        return await self.fetchrow("INSERT INTO Guilds (id, owner_id, prefix) VALUES ($1, $2, $3) RETURNING *;", id, owner_id, "hc!")

    async def fetch_guild(self, id: int, owner_id: int):
        guild = await self.fetchrow("SELECT * FROM Guilds WHERE id = $1;", id)

        if not guild:
            guild = await self.create_guild(id, owner_id)

        return guild

    async def set_guild_prefix(self, id: int, prefix: str):
        await self.execute("UPDATE Guilds SET prefix = $1 WHERE id = $2;", prefix, id)

    async def create_restart(self, channel: int, message: int):
        await self.execute("UPDATE Restarts SET done = TRUE;")
        await self.execute("INSERT INTO Restarts (cid, mid) VALUES ($1, $2);", channel, message)

    async def get_restart(self):
        data = await self.fetchrow("SELECT * FROM Restarts WHERE done = FALSE;")
        await self.execute("UPDATE Restarts SET done = TRUE;")
        return data

    async def create_reminder(self, uid: int, gid: int, cid: int, mid: int, time: datetime, content: str):
        res = await self.fetchrow(
            "INSERT INTO Reminders (userid, gid, cid, mid, content, expires) VALUES ($1, $2, $3, $4, $5, $6) RETURNING id;",
            uid, gid, cid, mid, content, time,
        )

        return res["id"]

    async def get_expired_reminders(self):
        return await self.fetch("SELECT * FROM Reminders WHERE expired = FALSE;")

    async def mark_reminder_completed(self, id: int):
        await self.execute("UPDATE Reminders SET expired = TRUE WHERE id = $1;", id)
