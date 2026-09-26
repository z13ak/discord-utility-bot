"""Entry point - loads cogs, syncs slash commands, starts the bot."""

from __future__ import annotations

import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

import database

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("bot")

INITIAL_COGS = ("cogs.moderation", "cogs.utility", "cogs.tags")


class UtilityBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self) -> None:
        database.init_db()
        for extension in INITIAL_COGS:
            await self.load_extension(extension)
            log.info("Loaded extension: %s", extension)

        guild_id = os.getenv("DEV_GUILD_ID")
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            log.info("Synced %d command(s) to guild %s (instant, for development)", len(synced), guild_id)
        else:
            synced = await self.tree.sync()
            log.info("Synced %d global command(s) (can take up to an hour to propagate)", len(synced))

    async def on_ready(self) -> None:
        log.info("Logged in as %s (ID: %s)", self.user, self.user.id)
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="/help · zleak.dev")
        )


def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise SystemExit(
            "DISCORD_TOKEN is not set. Copy .env.example to .env and add your bot token."
        )

    bot = UtilityBot()
    asyncio.run(bot.start(token))


if __name__ == "__main__":
    main()
