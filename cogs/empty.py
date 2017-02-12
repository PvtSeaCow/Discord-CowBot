import asyncio
import discord
from discord.ext import commands
import cogs.utils.checks as checks

class empty:
    """No Commands"""
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    n = empty(bot)
    bot.add_cog(n)