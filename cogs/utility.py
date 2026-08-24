"""General utility commands: ping, userinfo, serverinfo, avatar."""

from __future__ import annotations

import time

import discord
from discord import app_commands
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping", description="Check the bot's latency.")
    async def ping(self, interaction: discord.Interaction) -> None:
        start = time.perf_counter()
        await interaction.response.send_message("Pinging...")
        elapsed_ms = (time.perf_counter() - start) * 1000
        await interaction.edit_original_response(
            content=f"Pong! Gateway: {self.bot.latency * 1000:.0f}ms · Round trip: {elapsed_ms:.0f}ms"
        )

    @app_commands.command(name="userinfo", description="Show information about a member.")
    @app_commands.describe(member="The member to look up (defaults to you)")
    async def userinfo(
        self, interaction: discord.Interaction, member: discord.Member | None = None
    ) -> None:
        member = member or interaction.user
        embed = discord.Embed(title=str(member), color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=str(member.id))
        embed.add_field(name="Joined server", value=discord.utils.format_dt(member.joined_at, "R"))
        embed.add_field(name="Account created", value=discord.utils.format_dt(member.created_at, "R"))
        roles = [role.mention for role in reversed(member.roles) if role.name != "@everyone"]
        embed.add_field(
            name=f"Roles ({len(roles)})",
            value=" ".join(roles[:15]) if roles else "None",
            inline=False,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Show information about this server.")
    async def serverinfo(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        embed = discord.Embed(title=guild.name, color=discord.Color.blurple())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Owner", value=str(guild.owner) if guild.owner else "Unknown")
        embed.add_field(name="Members", value=str(guild.member_count))
        embed.add_field(name="Channels", value=str(len(guild.channels)))
        embed.add_field(name="Roles", value=str(len(guild.roles)))
        embed.add_field(name="Created", value=discord.utils.format_dt(guild.created_at, "R"))
        embed.add_field(name="Boost level", value=str(guild.premium_tier))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Get a member's avatar.")
    @app_commands.describe(member="The member to look up (defaults to you)")
    async def avatar(
        self, interaction: discord.Interaction, member: discord.Member | None = None
    ) -> None:
        member = member or interaction.user
        embed = discord.Embed(title=f"{member.display_name}'s avatar", color=discord.Color.blurple())
        embed.set_image(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utility(bot))
