"""Moderation commands: warn, kick, ban, timeout, purge."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

import database


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="warn", description="Warn a member and log it.")
    @app_commands.describe(member="The member to warn", reason="Why they're being warned")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(
        self, interaction: discord.Interaction, member: discord.Member, reason: str
    ) -> None:
        if member.bot:
            await interaction.response.send_message("You can't warn a bot.", ephemeral=True)
            return
        if member.id == interaction.user.id:
            await interaction.response.send_message("You can't warn yourself.", ephemeral=True)
            return

        warning_id = database.add_warning(
            interaction.guild_id, member.id, interaction.user.id, reason
        )
        embed = discord.Embed(
            title="Member warned",
            description=f"{member.mention} has been warned.",
            color=discord.Color.orange(),
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"Warning #{warning_id}")
        await interaction.response.send_message(embed=embed)

        try:
            await member.send(
                f"You were warned in **{interaction.guild.name}** for: {reason}"
            )
        except discord.Forbidden:
            pass

    @app_commands.command(name="warnings", description="List a member's warnings.")
    @app_commands.describe(member="The member to check")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warnings(self, interaction: discord.Interaction, member: discord.Member) -> None:
        rows = database.get_warnings(interaction.guild_id, member.id)
        if not rows:
            await interaction.response.send_message(
                f"{member.mention} has no warnings.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"Warnings for {member.display_name}",
            color=discord.Color.orange(),
        )
        for row in rows[:10]:
            embed.add_field(
                name=f"#{row['id']} — {row['created_at']}",
                value=row["reason"],
                inline=False,
            )
        if len(rows) > 10:
            embed.set_footer(text=f"Showing 10 of {len(rows)} warnings")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="clearwarnings", description="Clear all warnings for a member.")
    @app_commands.describe(member="The member to clear warnings for")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def clearwarnings(self, interaction: discord.Interaction, member: discord.Member) -> None:
        deleted = database.clear_warnings(interaction.guild_id, member.id)
        await interaction.response.send_message(
            f"Cleared {deleted} warning(s) for {member.mention}.", ephemeral=True
        )

    @app_commands.command(name="timeout", description="Timeout a member.")
    @app_commands.describe(member="The member to time out", minutes="Duration in minutes", reason="Reason")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        minutes: app_commands.Range[int, 1, 40320],
        reason: str = "No reason provided",
    ) -> None:
        import datetime

        try:
            await member.timeout(
                datetime.timedelta(minutes=minutes), reason=f"{interaction.user}: {reason}"
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to timeout that member.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"{member.mention} has been timed out for {minutes} minute(s). Reason: {reason}"
        )

    @app_commands.command(name="kick", description="Kick a member from the server.")
    @app_commands.describe(member="The member to kick", reason="Reason")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(
        self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"
    ) -> None:
        try:
            await member.kick(reason=f"{interaction.user}: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to kick that member.", ephemeral=True
            )
            return
        await interaction.response.send_message(f"{member.mention} was kicked. Reason: {reason}")

    @app_commands.command(name="ban", description="Ban a member from the server.")
    @app_commands.describe(member="The member to ban", reason="Reason")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(
        self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"
    ) -> None:
        try:
            await member.ban(reason=f"{interaction.user}: {reason}", delete_message_days=0)
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to ban that member.", ephemeral=True
            )
            return
        await interaction.response.send_message(f"{member.mention} was banned. Reason: {reason}")

    @app_commands.command(name="purge", description="Bulk delete recent messages in this channel.")
    @app_commands.describe(amount="Number of messages to delete (1-100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(
        self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100]
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Deleted {len(deleted)} message(s).", ephemeral=True)

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            message = "You don't have permission to use this command."
        else:
            message = f"Something went wrong: {error}"

        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderation(bot))
