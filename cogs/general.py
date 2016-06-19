import asyncio
import discord
from discord.ext import commands
import cogs.utils.checks as checks
import praw
import datetime
import time
import requests
from time import sleep

class general:
    """General Commands"""
    def __init__(self, bot):
        self.reddit = praw.Reddit('Cow for Discord by Moe Sea Cow (Anime Discord)')
        self.reddit.set_oauth_app_info("SNhrW_wB9ZRPFQ", 'aHC9_YP0vgptp4Tc-h-JsVarDJU', redirect_uri='http://127.0.0.1:65010/authorize_callback')
        self.bot = bot

    @commands.command(aliases=["ver"], hidden=True)
    async def version(self):
        '''Shows the version of discord.'''
        await self.bot.say('**Discord Version:** `'+discord.__version__+'` **Discord.py Version:** `'+'v0.10.0'+'`')

    @commands.command(aliases=['pong'], pass_context=True)
    async def ping(self, ctx):
        ms = datetime.datetime.now().microsecond - ctx.message.timestamp.now().microsecond
        t1 = time.perf_counter()
        await self.bot.type()
        t2 = time.perf_counter()
        await self.bot.say("pong: `{}ms`".format(round((t2-t1)*1000)))
        if ctx.message.author.id == self.bot.user.id:
            sleep(3)
            await self.bot.delete_message(ctx.message)

    @commands.command(hidden=True, name="geturl")
    async def get_url(self):
        await self.bot.say('Have fun!!\nhttps://discordapp.com/oauth2/authorize?client_id=192691494254018570&scope=bot&permissions=0')
        pass

    @commands.command(hidden=True, name="gold")
    async def _gold(self):
        msg = await self.bot.say('')
        pass

def setup(bot):
    n = general(bot)
    bot.add_cog(n)
