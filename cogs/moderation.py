import asyncio
import discord
from discord.ext import commands
from time import sleep
import cogs.utils.checks as checks
import json
import sys
import os
import time
import configparser
import pip
import subprocess
import pyperclip
import logging
import traceback

from multiprocessing import Pool

import datetime
from dateutil.relativedelta import relativedelta

global config, serverconfig
config = configparser.ConfigParser()
serverconfig = configparser.ConfigParser()
config.read('./data/config/config.ini')

date_started = datetime.datetime.now()

def create_server_ini(server, surpress=False):
    if surpress == False:
        print('Creating ini file for \'{}\' ({})'.format(server.name, server.id))
    serverfp = "./data/config/servers/{}".format(server.id)
    if os.path.exists(serverfp) == False:
        os.makedirs(serverfp)
        f = open(serverfp+'/'+server.name, 'w')
        f.close()
    if not os.path.isfile(serverfp+"/server_settings.ini"):
        f = open(serverfp+"/server_settings.ini", 'w')
        f.close()
    if os.path.exists(serverfp) and os.path.getsize(serverfp+"/server_settings.ini") != 0:
        if surpress == False:
            print('\tini file already made!! Skipping!!'.format(server.name, server.id))
    else:
        f = open('data/config/whitelist_server.txt', 'r')
        whitelist = f.read()
        f.close()
        if server.id in whitelist:
            ignore = 'false'
        else:
            ignore = 'true'
        tempconfig = configparser.ConfigParser()
        tempconfig.read(serverfp+"/server_settings.ini")
        tempconfig['settings'] = {
        'nsfw': 'false',
        'ignore': ignore,
        'log': 'false',
        'msgjoin': 'false',
        'msgjoin_str': 'Welcome {0.mention} to our server!! Please Read the Rules and Have Fun!!!'
        }
        with open(serverfp+"/server_settings.ini", 'w') as configfile:
            tempconfig.write(configfile)
        if surpress == False:
            print('\t\tCreated ini!!')
        del tempconfig

def get_value(file, section, option):
    tempconfig = configparser.ConfigParser()
    tempconfig.read(file)
    return tempconfig[section][option]

class moderation:
    """Moderation Commands!"""
    def __init__(self, bot):
        self.bot = bot
        self.pool = Pool(processes=1)

    @commands.command(name='shutdown',aliases=['shut','Shutdown','Shut','SHUT','SHUTDOWN'], hidden=True, pass_context=True)
    @checks.is_owner()
    async def _shutdown(self, ctx):
        await self.shutdown(ctx)

    @commands.command(name='uptimeold', hidden=True, pass_context=True, enabled=False)
    @checks.is_owner()
    @asyncio.coroutine
    def uptime_old(self, ctx):
        now = datetime.datetime.now()
        ago = relativedelta(now, date_started)
        if ago.days == 0:
            ago_days = ""
        else:
            ago_days = str(ago.days)+" days, "
        if ago.hours == 0:
            ago_hours = ""
        else:
            ago_hours = str(ago.hours)+" hours, "
        if ago.minutes == 0:
            ago_minutes = ""
        else:
            ago_minutes = str(ago.minutes)+" minutes, "
        ago_seconds = str(ago.seconds)+" seconds"
        ago_all = ago_days+ago_hours+ago_minutes+ago_seconds
        yield from self.bot.say("**Uptime:** {}".format(ago_all))

    @commands.command(name="uptime", hidden=True, pass_context=True)
    @checks.is_owner_or_admin()
    @asyncio.coroutine
    def uptime(self, ctx):
        now = datetime.datetime.now()
        ago = relativedelta(now, date_started)
        ago_all = "{0.days} days, {0.hours} hours, {0.minutes} minutes, and {0.seconds} seconds".format(ago)
        embed = discord.Embed(title="Uptime:", description=ago_all)
        if ctx.message.author != ctx.message.server.me:
            embed.set_footer(text="{0.name}#{0.discriminator}".format(ctx.message.author))
        yield from self.bot.say(embed=embed)

    @commands.group()
    @checks.is_owner()
    async def cogs(self):
        pass

    @cogs.command(name="list")
    async def list_cogs(self):
        all_cogs = [f for f in os.listdir("./cogs") if os.path.isfile(os.path.join("./cogs", f))]
        loaded = []
        unloaded = []
        for cog in all_cogs:
            cog = cog.split('.')[0]
            ccog = self.bot.get_cog(cog.lower())
            if ccog:
                loaded.append(cog.replace("_"," "))
            else:
                unloaded.append(cog.replace("_"," "))
        embed = discord.Embed(title="Current Cogs!", description=str("Total Cogs: {} | Loaded: {} | Unloaded: {}".format(len(all_cogs), len(loaded), len(unloaded))).title())
        if len(loaded) != 0:
            embed.add_field(name="Loaded Cogs:", value=str(", ".join(loaded)).title(), inline=False)
        if len(unloaded) != 0:
            embed.add_field(name="Unloaded Cogs:", value=str(", ".join(unloaded)).title(), inline=False)
        await self.bot.say(embed=embed)
        pass

    @cogs.command(name='unload', hidden=True, pass_context=True, aliases=['u','un'])
    async def _unload(self, ctx, *, cogs : str = None):
        await self.bot.say('__***Unloading cogs...***__', delete_after=4)
        if cogs != None:
            cogs = cogs.split(" ")
        elif cogs == None:
            cogs = [f for f in os.listdir("./cogs") if os.path.isfile(os.path.join("./cogs", f))]

        temp = [cog for cog in cogs]
        temp2 = []
        for cog in cogs:
            cog = cog.lower()
            if self.bot.get_cog(cog):
                self.bot.unload_extension("cogs."+cog.replace('.py',''))
            else:
                temp2.append(cog)
                temp.remove(cog)
        extra = ''
        if len(temp2) >= 1:
            extra = ", ".join(temp2)
            extra = "\n__***Couldn't load cogs: {}***__".format(extra)
        msg = '__***Unloaded Cogs: {}***__{}'.format(str(", ".join(temp)).replace("_"," ").title(), extra)
        await self.bot.say(msg, delete_after=4)
        del temp
        del temp2

    @cogs.command(name='reload', hidden=True, pass_context=True, aliases=['r','re'])
    async def _reload(self, ctx, *, cogs : str = None):
        msg1 = await self.bot.say('__***Reloading cogs...***__', delete_after=10)
        if cogs != None:
            cogs = cogs.split(" ")
        elif cogs == None:
            cogs = [f for f in os.listdir("./cogs") if os.path.isfile(os.path.join("./cogs", f))]

        temp = [cog for cog in cogs]
        for cog in cogs:
            self.bot.unload_extension("cogs."+cog.replace('.py',''))
        logging.info("Unloaded: {}".format(", ".join(temp)))
        del temp
        await asyncio.sleep(1)
        load_cogs = []
        not_loaded = []
        for cog in cogs:
            cog_str = cog.replace('.py','')
            try:
                self.bot.load_extension("cogs."+cog_str)
            except ImportError:
                await self.bot.say("`{}` is not a cog or it doesn't exist".format(cog_str))
                not_loaded.append(cog_str)
            except Exception as e:
                not_loaded.append(cog_str)
                if (len(cogs) == 1):
                    raise
            else:
                load_cogs.append(cog_str)
        temp = []
        if len(load_cogs) != 0:
            msg_not_loaded = '***Cogs Reloaded:*** `{}`'.format(", ".join(load_cogs))
            temp.append(msg_not_loaded)
        if len(not_loaded) != 0:
            msg_loaded = '***Cogs Not Loaded:*** `{}`'.format(", ".join(not_loaded))
            temp.append(msg_loaded)
        logging.info(" | ".join(temp).upper())
        msg2 = await self.bot.say(" | ".join(temp).upper(), delete_after=5)
        del temp

    @commands.command(aliases=["away", "status"], pass_context=True)
    @checks.is_owner_or_admin()
    async def setstatus(self, ctx, *, message : str = None):
        with open('data/game.txt', 'w+') as f:
            if message != None:
                f.write(' '.join(message))
            else:
                f.write('')
        if ctx.message.server.me.id == "105800900521570304":
            status = discord.Status.invisible
        else:
            status = discord.Status.online
        if message != None:
            await self.bot.change_presence(game=discord.Game(name=message), status=status)
        elif message == None:
            await self.bot.change_presence(game=None, status=status)

    @commands.command(name='msgsent', pass_context=True, hidden=True)
    @checks.is_owner()
    async def msg_sent(self, ctx, *, member : discord.Member = None):
        if member == None:
            member = ctx.message.author
        counter = 0
        async for message in self.bot.logs_from(ctx.message.channel, limit=500):
            if message.author == member:
                counter += 1
        await self.bot.say('Number of Messages sent: `'+str(counter)+' out of 500 messages`')
        sleep(0.5)
        await self.bot.delete_message(ctx.message)

    @commands.command(name='eval', pass_context=True, hidden=True)
    @checks.is_owner()
    @asyncio.coroutine
    def _eval(self, ctx, *, content : str):
        global_vars = globals().copy()
        global_vars['bot'] = self.bot
        global_vars['ctx'] = ctx
        global_vars['message'] = ctx.message
        global_vars['author'] = ctx.message.author
        global_vars['channel'] = ctx.message.channel
        if ctx.message.server:
            global_vars['server'] = ctx.message.server
            global_vars['me'] = ctx.message.server.me
        result = eval(content, global_vars, locals())
        if asyncio.iscoroutine(result):
            result = yield from result

        msg = str(result)

        yield from self.bot.say('`'+str(msg)+'`')

    @commands.command(name='exec', pass_context=True, hidden=True)
    @checks.is_owner()
    @asyncio.coroutine
    def _exec(self, ctx, *, content : str):
        global_vars = globals().copy()
        global_vars['bot'] = self.bot
        global_vars['ctx'] = ctx
        global_vars['message'] = ctx.message
        global_vars['author'] = ctx.message.author
        global_vars['channel'] = ctx.message.channel
        if ctx.message.server:
            global_vars['server'] = ctx.message.server
            global_vars['me'] = ctx.message.server.me
        result = exec(content, global_vars, locals())
        if asyncio.iscoroutine(result):
            result = yield from result
        msg = str(result)
        #yield from self.bot.say('`'+str(msg)+'`')

    @commands.command(name="osexec", aliases=["os"], hidden=True)
    @checks.is_owner()
    @asyncio.coroutine
    def _exec_os_commands(self, *, command : str = None):
        if command == None:
            yield from self.bot.say("Error: No Command to Issue")
        yield from self.bot.say("*Running Command...*")
        try:
            output = subprocess.run(command, shell=True, stdout=subprocess.PIPE).stdout
        except subprocess.CalledProcessError as e:
            yield from self.bot.say(str(e))
            return
        except:
            raise
        else:
            yield from self.bot.say("```py\n{}```".format(str(output.decode("utf-8"))))

    @commands.command(name="sudo", aliases=["su"], hidden=True)
    @checks.is_owner()
    @asyncio.coroutine
    def _exec_os_sudo_commands(self, *, command : str = None):
        if command == None:
            raise Exception("Argument \"command\" is blank")
        if command.startswith("sudo"):
            command = " ".join(command.split(" ")[1:])
        yield from self.bot.say("*Running Sudo Command...*")
        try:
            output = subprocess.run("""echo "penny123" | sudo -S """+command, shell=True, stdout=subprocess.PIPE).stdout
        except subprocess.CalledProcessError as e:
            yield from self.bot.say(str(e))
            return
        except:
            raise
        else:
            yield from self.bot.say("```py\n{}```".format(str(output.decode("utf-8")).replace("\"penny123\"", "********")))

    @commands.command(name='prune', pass_context=True, hidden=True)
    @checks.is_owner_or_admin()
    async def prune(self, ctx, amount, *, user : discord.Member):
        print('Pruning '+amount+' msgs from '+user.name)
        shit = await self.bot.purge_from(ctx.message.channel, limit=int(amount), check=None)
        for msg in shit:
            await self.bot.delete_message(msg)
        pass

    @commands.command(name='getmessage', pass_context=True, hidden=True, aliases=['gm', 'get_message'])
    @checks.is_owner()
    async def _get_message(self, ctx, *, msgid : str):
        msg = await self.bot.get_message(ctx.message.channel, msgid)
        await self.bot.say('`'+msg.content+'`')

    @commands.command(name='leave', pass_context=True, hidden=True)
    @checks.is_owner()
    async def _leave_server(self, ctx):
        if ctx.message.author != ctx.message.server.me:
            return
        await self.bot.say('**WARNING:** YOU ARE ABOUT TO LEAVE THIS SERVER!! TYPE `leave` IN 5 SECONDS TO LEAVE!!')
        msg = await self.bot.wait_for_message(timeout=5,author=ctx.message.server.me, content='leave')
        if ctx.message.server.me == ctx.message.server.owner:
            await self.bot.say('***You can\'t leave your own server***')
        elif msg == None:
            await self.bot.say('***LEAVE CANCELLED***')
        elif msg.content == 'leave':
            await self.bot.leave_server(ctx.message.server)
        else:
            pass
        pass

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def update(self, ctx):
        await self.bot.say("```Updating Discord...```")
        subprocess.call("""echo "penny123" | sudo -SH python3 -m pip install -U discord.py""", shell=True)
        await self.bot.say('```Update Complete!!\nShutting Down...```')
        await self.shutdown(ctx)

    async def shutdown(self, ctx):
        await self.bot.send_message(ctx.message.channel ,"___***Bot shutting down...***___")
        await self.bot.logout()

    @commands.group()
    @checks.is_owner()
    async def settings(self):
        pass

    @settings.command(name='list', aliases=['l'], pass_context=True)
    @asyncio.coroutine
    def _list_settings_for_server(self, ctx, *, server_id : str = None):
        if server_id == None:
            server = ctx.message.server
        else:
            server = self.bot.get_server(server_id)
        fp = "./data/config/servers/"+server.id
        if not os.path.exists(fp):
            yield from self.bot.say("***Server Config File not made!***\n*Run `{}settings createfiles`!!*".format(self.bot.command_prefix[0]))
            return
        serverconfig.read(fp+"/server_settings.ini")
        shit = '```md\n'
        shit = shit+server.name+'\n'
        for setting in serverconfig['settings']:
            if setting == 'msgjoin_str' and serverconfig['settings']['msgjoin'].lower() == "false":
                pass
            else:
                shit = shit+"[{0}]: {1}\n".format(setting.upper(), serverconfig['settings'][setting].title())
        shit = shit+'```'
        yield from self.bot.say(shit)
        pass

    @settings.command(name='createfiles')
    async def _settings_create_serverfiles(self):
        serverlist = self.bot.servers
        for server in serverlist:
            create_server_ini(server)

    @settings.command(name='set', pass_context=True)
    @asyncio.coroutine
    def _set_option_for_single_server(self, ctx, setting, value):
        yield from self.set_option(ctx, setting, value)

    @commands.command(name="enable", pass_context=True)
    @checks.is_owner_or_admin()
    async def enable_server_commands(self, ctx):
        await self.set_option(ctx, "ignore", "false")

    @commands.command(name="disable", pass_context=True)
    @checks.is_owner_or_admin()
    async def disable_server_commands(self, ctx):
        await self.set_option(ctx, "ignore", "true")

    @asyncio.coroutine
    def set_option(self, ctx, setting, value):
        fp = "./data/config/servers/"+ctx.message.server.id
        if not os.path.exists(fp):
            yield from self.bot.say("***Server Config File not made!***\n*Run `{}settings createfiles`!!*".format(self.bot.command_prefix[0]))
            return
        serverconfig.read(fp+"/server_settings.ini")
        serverconfig.set("settings", setting, value)
        file1 = open(fp+"/server_settings.ini", 'w+')
        serverconfig.write(file1)
        file1.close()
        yield from self.bot.say("**Set `{}` as `{}`**".format(setting, value))
        pass

    @settings.command(name='setall', pass_context=True)
    @asyncio.coroutine
    def _set_option_for_all_servers(self, ctx, setting, value):
        section = 'settings'
        for server in self.bot.servers:
            fp = "./data/config/servers/"+server.id
            if not os.path.exists(fp):
                yield from self.bot.say("***Server Config File not made!***\n*Run `{}settings createfiles`!!*".format(self.bot.command_prefix[0]))
                return
            serverconfig.read(fp+"/server_settings.ini")
            serverconfig.set("settings", setting, value)
            file1 = open(fp+"/server_settings.ini", 'w+')
            serverconfig.write(file1)
            file1.close()
            pass
        yield from self.bot.say("**Set `{}` as `{}` on all server configs**".format(setting, value))
        pass

    @settings.group(name='get')
    async def get(self):
        pass

    @commands.command(name='botinfo', pass_context=True)
    @asyncio.coroutine
    def get_bot_info(self, ctx):
        """Show Info About the Bot"""
        desc = self.bot.description
        main_prefix = self.bot.command_prefix[0]
        num_of_servers = str(len(list(self.bot.servers)))
        author = "{0.name}#{0.discriminator}".format(ctx.message.server.me)

        #info = "```md\n("+desc+")\n[Main Prefix]: "+main_prefix+"\n[Number of Connected Servers]: "+num_of_servers+"\n[Author]: "+author+"```"
        #yield from self.bot.say(info)
        embed = discord.Embed(title="Cow's Bot", description=desc)
        embed.add_field(name="Main Prefix:", value=main_prefix)
        embed.add_field(name="Number of Connected Servers:", value=main_prefix)
        embed.set_footer(icon=ctx.message.server.me.avatar_url, text=author)
        yield from self.bot.say(embed=embed)
        pass

    @commands.command(name="copy")
    @asyncio.coroutine
    @checks.is_owner()
    def copy_into_clipboard(self, *, to_copy = None):
        if to_copy == None:
            yield from self.bot.say("*Nothing to copy!*")
            return
        pyperclip.copy(str(to_copy))
        yield from self.bot.say("***Copied***")
        pass

    @commands.command(name="paste")
    @asyncio.coroutine
    @checks.is_owner()
    def paste_from_clipboard(self):
        yield from self.bot.say("```{}```".format(pyperclip.paste()))
        pass

def setup(bot):
    n = moderation(bot)
    bot.add_cog(n)