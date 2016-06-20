import asyncio
import discord
from discord.ext import commands
from time import sleep
import cogs.utils.checks as checks
import json

class mod:
    """Moderation Commands!"""
    def __init__(self, bot):
        self.bot = bot

        global prefix
        prefix = bot.command_prefix

    @commands.command(aliases=['rst','shutdown'], hidden=True)
    @checks.mod_or_permissions()
    async def restart(self):
        '''Restarts Bot.'''
        await self.bot.say("___***Bot Restarting...***___")
        await self.bot.logout()
        try:
            exit
        except SystemExit: #clean exit
            pass

    @commands.command(name='update', hidden=True, pass_context=True)
    @checks.mod_or_permissions()
    async def _update(self, ctx):
        '''does a git pull and restarts.'''
        pass #Todo

    @commands.command(name='reload', hidden=True, pass_context=True)
    @checks.mod_or_permissions()
    async def _reload(self, ctx, *cogs):
        '''Reloads Cogs.'''
        for cog in cogs:
            try:
                self.bot.get_cog(cog)
            except:
                self.bot.say('`'+cog+'` is not a cog.')
        if cogs != ():
            msg1 = await self.bot.say('__***Reloading {0}...***__'.format(', '.join(cogs)))
            for cog in cogs:
                self.bot.unload_extension('cogs.'+cog)
            sleep(1)
            try:
                for cog in cogs:
                    self.bot.load_extension('cogs.'+str(cog))
                msg2 = await self.bot.say('__***Cogs Reloaded! :ok_hand:***__')
                print("Reloaded the following cogs: "+', '.join(cogs))
                sleep(2)
                await self.bot.delete_message(msg1)
                sleep(0.5)
                await self.bot.delete_message(msg2)
                sleep(0.5)
                await self.bot.delete_message(ctx.message)
            except:
                msg2 = await self.bot.say('__***:x: Cogs COULDN\'T reload!!! :x:***__')
                sleep(2)
                await self.bot.delete_message(msg1)
                sleep(0.5)
                await self.bot.delete_message(msg2)
                sleep(0.5)
                await self.bot.delete_message(ctx.message)
                raise
        else:
            msg1 = await self.bot.say('__***Reloading cogs...***__')
            self.bot.unload_extension('cogs.music')
            self.bot.unload_extension('cogs.general')
            self.bot.unload_extension('cogs.moderation')
            self.bot.unload_extension('cogs.nsfw')
            sleep(0.5)
            self.bot.load_extension('cogs.moderation')
            try:
                self.bot.load_extension('cogs.music')
                self.bot.load_extension('cogs.general')
                self.bot.load_extension('cogs.nsfw')
            except:
                msg2 = await self.bot.say('__***:x: Cogs COULDN\'T reload!!! :x:***__')
                sleep(2)
                await self.bot.delete_message(msg1)
                sleep(0.5)
                await self.bot.delete_message(msg2)
                sleep(0.5)
                await self.bot.delete_message(ctx.message)
                raise
            else:
                print("Reloaded the all cogs.")
                msg2 = await self.bot.say('__***Cogs Reloaded! :ok_hand:***__')
                sleep(2)
                await self.bot.delete_message(msg1)
                sleep(0.5)
                await self.bot.delete_message(msg2)
                sleep(0.5)
                await self.bot.delete_message(ctx.message)

    @commands.group(pass_context=True, discription='Use \'ignore add\' to add the current channel to the ignore list.')
    @checks.mod_or_permissions()
    async def ignore(self, ctx):
        pass

    @ignore.command(name='add', pass_context=True)
    async def add_to_ignore(self, ctx, *channels):
        if ctx.message.channel_mentions:
            f = open('data\\config\\ignore_channels.txt', 'a+')
            f.write(f.read()+'\n'.join(str(channel.id) for channel in ctx.message.channel_mentions)+'\n')
            f.close()
            msg = await self.bot.say(', '.join(channel.mention for channel in ctx.message.channel_mentions)+" added to the ignore list.")
            sleep(2)
            await self.bot.delete_message(msg)
            sleep(0.5)
            await self.bot.delete_message(ctx.message)
        else:
            f = open('data\\config\\ignore_channels.txt', 'a+')
            f.write(f.read()+str(ctx.message.channel.id)+'\n')
            f.close()
            msg = await self.bot.say(ctx.message.channel.mention+" added to the ignore list.")
            sleep(2)
            await self.bot.delete_message(msg)
            sleep(0.5)
            await self.bot.delete_message(ctx.message)

    @ignore.command(name='rem', aliases=['remove'], pass_context=True)
    async def remove_from_ignore(self, ctx):
        f = open('data\\config\\ignore_channels.txt', 'r')
        thing = f.read()
        f.close()
        if str(ctx.message.channel.id) in thing:
            f = open('data\\config\\ignore_channels.txt', 'w+')
            f.write(thing.replace('\n'+str(ctx.message.channel.id),''))
            f.close()
            msg = await self.bot.say(ctx.message.channel.mention+" removed from the ignore list.")
            sleep(2)
            await self.bot.delete_message(msg)
            sleep(0.5)
            await self.bot.delete_message(ctx.message)
        else:
            msg = await self.bot.say(ctx.message.channel.mention+'is not on the ignore list.')
            sleep(2)
            await self.bot.delete_message(msg)
            sleep(0.5)
            await self.bot.delete_message(ctx.message)
        pass

    @ignore.command(name='list', pass_context=True)
    async def list_ignore(self, ctx):
        f = open('data\\config\\ignore_channels.txt', 'r')
        thing = f.read()
        f.close()
        thing = thing.split('\n')
        thing2 = "Channels in the ignore list: "+', '.join(self.bot.get_channel(int(thing2)).mention for thing2 in thing)
        await self.bot.say(thing2)

    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def name(self, ctx, *name):
        await self.bot.edit_profile(username=' '.join(name))

    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def setava(self, ctx, imgfile):
        f = open(imgfile, 'rb')
        f2 = f.read()
        f.close()
        await self.bot.edit_profile(avatar=f2)
        pass

    @commands.command(name='eval', pass_context=True, hidden=True)
    @checks.is_owner()
    async def _eval(self, ctx, *content):
        message = ctx.message
        await self.bot.say('`'+str(eval(' '.join(content)))+'`')

    @commands.command(name='exec', pass_context=True, hidden=True)
    @checks.is_owner()
    async def _exec(self, ctx):
        message = ctx.message
        content = content[1].replace('python\n', '')
        #content = message.content
        #content = content.replace(self.bot.command_prefix[0]+'exec ```python','')
        #content = content.replace('```', '')
        await self.bot.say('EXECUTING: `'+str(content)+'`')
        sleep(1)
        try:
            #asyncio.create_subprocess_exec(msg)
            exec_command(content)
            #exec(msg)
        except Exception as e:
            await self.bot.say('UNABLE TO EXECUTE: ```py\n'+ type(e).__name__ + e + '\n```')
            raise

def setup(bot):
    n = mod(bot)
    bot.add_cog(n)
