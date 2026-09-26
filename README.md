# discord-utility-bot

A moderation and utility Discord bot built with `discord.py` 2.x, slash commands, and SQLite persistence.

## Features

- **Moderation** - `/warn`, `/warnings`, `/clearwarnings`, `/timeout`, `/kick`, `/ban`, `/purge`, all permission-gated and logged to SQLite.
- **Utility** - `/ping`, `/userinfo`, `/serverinfo`, `/avatar`.
- **Tags** - `/tag create|get|delete|list`, reusable text snippets scoped per server.
- Cog-based architecture, centralized error handling, structured logging.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env and add your bot token (from the Discord Developer Portal)
python bot.py
```

Set `DEV_GUILD_ID` in `.env` to a test server's ID while developing — guild-scoped
commands sync instantly, whereas global commands can take up to an hour to propagate.

## Project layout

```
bot.py              entry point — loads cogs, syncs commands, starts the bot
database.py          SQLite helpers (warnings, tags)
cogs/moderation.py    warn/kick/ban/timeout/purge
cogs/utility.py       ping/userinfo/serverinfo/avatar
cogs/tags.py          custom tag system
```

## Required bot permissions/intents

Enable the **Server Members** and **Message Content** privileged intents in the
Developer Portal, and invite the bot with `Kick Members`, `Ban Members`,
`Moderate Members`, `Manage Messages`, and `Send Messages` permissions.
