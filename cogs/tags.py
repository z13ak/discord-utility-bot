"""Custom reusable text snippets, stored per-server."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

import database


class Tags(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    tag_group = app_commands.Group(name="tag", description="Manage and use reusable text snippets.")

    @tag_group.command(name="create", description="Create a new tag.")
    @app_commands.describe(name="Tag name", content="What the tag should say")
    async def create(self, interaction: discord.Interaction, name: str, content: str) -> None:
        if len(name) > 50:
            await interaction.response.send_message("Tag names must be 50 characters or fewer.", ephemeral=True)
            return

        created = database.create_tag(interaction.guild_id, name, content, interaction.user.id)
        if created:
            await interaction.response.send_message(f"Tag `{name.lower()}` created.")
        else:
            await interaction.response.send_message(
                f"A tag named `{name.lower()}` already exists.", ephemeral=True
            )

    @tag_group.command(name="get", description="Show a tag's content.")
    @app_commands.describe(name="Tag name")
    async def get(self, interaction: discord.Interaction, name: str) -> None:
        row = database.get_tag(interaction.guild_id, name)
        if row is None:
            await interaction.response.send_message(f"No tag named `{name.lower()}`.", ephemeral=True)
            return
        await interaction.response.send_message(row["content"])

    @tag_group.command(name="delete", description="Delete a tag.")
    @app_commands.describe(name="Tag name")
    async def delete(self, interaction: discord.Interaction, name: str) -> None:
        row = database.get_tag(interaction.guild_id, name)
        is_mod = interaction.user.guild_permissions.manage_guild
        if row is None:
            await interaction.response.send_message(f"No tag named `{name.lower()}`.", ephemeral=True)
            return
        if row["created_by"] != interaction.user.id and not is_mod:
            await interaction.response.send_message("Only the tag's creator or a moderator can delete it.", ephemeral=True)
            return

        database.delete_tag(interaction.guild_id, name)
        await interaction.response.send_message(f"Tag `{name.lower()}` deleted.")

    @tag_group.command(name="list", description="List every tag on this server.")
    async def list_tags(self, interaction: discord.Interaction) -> None:
        rows = database.list_tags(interaction.guild_id)
        if not rows:
            await interaction.response.send_message("No tags yet — create one with `/tag create`.", ephemeral=True)
            return
        names = ", ".join(f"`{row['name']}`" for row in rows)
        await interaction.response.send_message(f"**Tags ({len(rows)}):** {names}", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Tags(bot))
