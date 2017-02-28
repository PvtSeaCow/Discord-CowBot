import asyncio
import discord
from discord.ext import commands
import cogs.utils.checks as checks
import cogs.moderation as moderation
import traceback
import datetime
import time
import os
import difflib

from discord.ext.commands.view import StringView
from discord.ext.commands.context import Context

import configparser

import logging

class events:
    """No Commands, mainly for async events."""
    def __init__(self, bot):
        config = configparser.ConfigParser()
        config.read('./data/config/config.ini')
        self.config = config
        self.bot = bot

    def __unload(self):
        logging.info("Cogs [events] successfully unloaded")

    async def on_ready(self):
        logging.info("Cogs [events] successfully loaded and enabled")

    @asyncio.coroutine
    def process_commands(self, message):
        bot = self.bot
        log_channel = bot.get_server("107883969424396288").get_channel("257926036728184832")
        error_channel = bot.get_server("107883969424396288").get_channel("257922447205072897")
        _internal_channel = message.channel
        _internal_author = message.author
        self = bot

        view = StringView(message.content)
        if self._skip_check(message.author, self.user):
            pass

        prefix = yield from self._get_prefix(message)
        invoked_prefix = prefix

        if not isinstance(prefix, (tuple, list)):
            if not view.skip_string(prefix):
                return
        else:
            invoked_prefix = discord.utils.find(view.skip_string, prefix)
            if invoked_prefix is None:
                return

        if invoked_prefix is "c." and message.author != message.server.me:
            return


        invoker = view.get_word()
        invoker_orig = invoker
        diff = difflib.get_close_matches(invoker, self.commands, n=1, cutoff=0.8)
        if diff != []:
            invoker = diff[0]
        tmp = {
            'bot': self,
            'invoked_with': invoker,
            'message': message,
            'view': view,
            'prefix': invoked_prefix
        }
        ctx = Context(**tmp)
        del tmp

        if invoker in self.commands:
            command = self.commands[invoker]
            self.dispatch('command', command, ctx)
            try:
                yield from command.invoke(ctx)
            except discord.ext.commands.errors.DisabledCommand as e:
                yield from self.say("*`{}` is disabled*".format(str(e).split(" ")[0]))
            except discord.ext.commands.errors.CheckFailure as e:
                yield from self.say("```You do not have permission for this command!```")
            except discord.ext.commands.errors.CommandOnCooldown as e:
                yield from self.say("```{}```".format(str(e)))
            except discord.ext.commands.errors.BadArgument as e:
                yield from self.say("```{}```".format(str(e)))
            except discord.ext.commands.errors.CommandError as e:
                ctx.command.dispatch_error(e, ctx)
                yield from self.say("An Error Has Occurred: ```py\n{}```".format(traceback.format_exc().replace("/home/seacow/Discord-Bot/","./").split("The above exception was the direct cause of the following exception:")[0]))
                if not message.author == message.server.me:
                    yield from self.send_message(error_channel,"{}```py\n{}```".format("\"{}\" produced an error on \"{}\" / \"{}\" | Invoked by \"{}\"".format(message.content, _internal_channel.name, _internal_channel.server.name, _internal_author.name+"#"+_internal_author.discriminator), traceback.format_exc().replace("/home/seacow/Discord-Bot/","./").replace("\"penny123\"", "********").split("The above exception was the direct cause of the following exception:")[0]))
            except discord.ext.commands.errors.MissingRequiredArgument as e:
                yield from self.say("```{}```".format(str(e)))
            except:
                pass
            else:
                self.dispatch('command_completion', command, ctx)
        elif invoker:
            close_matches = difflib.get_close_matches(invoker, self.commands)
            extra = ""
            if close_matches != []:
                extra = "\nDid you mean?: {}{}".format(invoked_prefix, ", {}".format(invoked_prefix).join(close_matches))
            yield from self.say("```\"{}\" is not a command{}```".format(invoked_prefix+invoker, extra))
            exc = discord.ext.commands.errors.CommandNotFound('Command "{}" is not found'.format(invoker))
            logging.warning('Command "{}" is not found'.format(invoker))
            self.dispatch('command_error', exc, ctx)

    def get_whitelist_servers(self, setting, output):
        whitelist = []
        for channel in list(self.bot.get_all_channels()):
            fp = ("./data/config/servers/"+channel.server.id+"/server_settings.ini")
            boolean = str(moderation.get_value(fp, 'settings', setting))
            if bool(boolean) == bool(output) and channel.server.id not in whitelist:
                whitelist.append(channel.server.id)
        return whitelist
    
    async def on_member_join(self, member):
        log_channel = self.bot.get_server("107883969424396288").get_channel("257926036728184832")
        error_channel = self.bot.get_server("107883969424396288").get_channel("257922447205072897")
        localtime = time.localtime()
        tm_mon = localtime.tm_mon
        tm_min = localtime.tm_min
        tm_mday = localtime.tm_mday
        tm_hour = localtime.tm_hour
        if localtime.tm_hour >= 13:
            hourmin = localtime.tm_hour - 12
            hourmin = str(hourmin)+":"+str(localtime.tm_min)+" PM"
        else:
            hourmin = str(localtime.tm_hour)+":"+str(localtime.tm_min)+" AM"
        msgtime = "[ "+"{0}/{1}/16 | {2} ".format(tm_mon,tm_mday,hourmin)+" ]\n"
        fp = ("./data/config/servers/"+member.server.id+"/server_settings.ini")
        boolean = moderation.get_value(fp, 'settings', 'ignore').lower()
        if boolean == 'false':
            ending = msgtime+"Member ({0}) Joined: {1}".format(member.name+"#"+member.discriminator, member.server.name+" ("+str(member.server.id)+")")
            begin = "=====================================\n"
            logging.info(ending)
            await self.bot.send_message(log_channel, "```{}```".format(ending))

    
    async def on_member_remove(self, member):
        log_channel = self.bot.get_server("107883969424396288").get_channel("257926036728184832")
        error_channel = self.bot.get_server("107883969424396288").get_channel("257922447205072897")
        localtime = time.localtime()
        tm_mon = localtime.tm_mon
        tm_min = localtime.tm_min
        tm_mday = localtime.tm_mday
        tm_hour = localtime.tm_hour
        if localtime.tm_hour >= 13:
            hourmin = localtime.tm_hour - 12
            hourmin = str(hourmin)+":"+str(localtime.tm_min)+" PM"
        else:
            hourmin = str(localtime.tm_hour)+":"+str(localtime.tm_min)+" AM"
        msgtime = "[ "+"{0}/{1}/16 | {2} ".format(tm_mon,tm_mday,hourmin)+" ]\n"
        fp = ("./data/config/servers/"+member.server.id+"/server_settings.ini")
        boolean = moderation.get_value(fp, 'settings', 'ignore').lower()
        if boolean == 'false':
            ending = msgtime+"Member ({0}) Left: {1}".format(member.name+"#"+member.discriminator, member.server.name+" ("+str(member.server.id)+")")
            begin = "=====================================\n"
            logging.info(begin+ending)
            await self.bot.send_message(log_channel, "```{}```".format(ending))

    
    async def on_member_ban(self, member):
        log_channel = self.bot.get_server("107883969424396288").get_channel("257926036728184832")
        error_channel = self.bot.get_server("107883969424396288").get_channel("257922447205072897")
        localtime = time.localtime()
        tm_mon = localtime.tm_mon
        tm_min = localtime.tm_min
        tm_mday = localtime.tm_mday
        tm_hour = localtime.tm_hour
        if localtime.tm_hour >= 13:
            hourmin = localtime.tm_hour - 12
            hourmin = str(hourmin)+":"+str(localtime.tm_min)+" PM"
        else:
            hourmin = str(localtime.tm_hour)+":"+str(localtime.tm_min)+" AM"
        msgtime = "[ "+"{0}/{1}/16 | {2} ".format(tm_mon,tm_mday,hourmin)+" ]\n"
        fp = ("./data/config/servers/"+member.server.id+"/server_settings.ini")
        boolean = moderation.get_value(fp, 'settings', 'ignore').lower()
        if boolean == 'false':
            ending = msgtime+"Member ({0}) got banned from: {1}".format(member.name+"#"+member.discriminator, member.server.name+" ("+str(member.server.id)+")")
            begin = "=====================================\n"
            logging.info(ending)
            await self.bot.send_message(log_channel, "```{}```".format(ending))
        pass

    
    async def on_member_unban(self, server, user):
        log_channel = self.bot.get_server("107883969424396288").get_channel("257926036728184832")
        error_channel = self.bot.get_server("107883969424396288").get_channel("257922447205072897")
        localtime = time.localtime()
        tm_mon = localtime.tm_mon
        tm_min = localtime.tm_min
        tm_mday = localtime.tm_mday
        tm_hour = localtime.tm_hour
        if localtime.tm_hour >= 13:
            hourmin = localtime.tm_hour - 12
            hourmin = str(hourmin)+":"+str(localtime.tm_min)+" PM"
        else:
            hourmin = str(localtime.tm_hour)+":"+str(localtime.tm_min)+" AM"
        msgtime = "[ "+"{0}/{1}/16 | {2} ".format(tm_mon,tm_mday,hourmin)+" ]\n"
        fp = ("./data/config/servers/"+server.id+"/server_settings.ini")
        boolean = moderation.get_value(fp, 'settings', 'ignore').lower()
        if boolean == 'false':
            begin = "=====================================\n"
            ending = msgtime+"Member ({0}) got unbanned from: {1}".format(user.name+"#"+user.discriminator, server.name+" ("+str(server.id)+")")
            logging.info(ending)
            await self.bot.send_message(log_channel, "```{}```".format(ending))
        pass

    
    async def on_server_join(self, server):
        log_channel = self.bot.get_server("107883969424396288").get_channel("257926036728184832")
        error_channel = self.bot.get_server("107883969424396288").get_channel("257922447205072897")
        moderation.create_server_ini(server, True)
        localtime = time.localtime()
        tm_mon = localtime.tm_mon
        tm_min = localtime.tm_min
        tm_mday = localtime.tm_mday
        tm_hour = localtime.tm_hour
        if localtime.tm_hour >= 13:
            hourmin = localtime.tm_hour - 12
            hourmin = str(hourmin)+":"+str(localtime.tm_min)+" PM"
        else:
            hourmin = str(localtime.tm_hour)+":"+str(localtime.tm_min)+" AM"
        msgtime = "[ "+"{0}/{1}/16 | {2} ".format(tm_mon,tm_mday,hourmin)+" ]\n"
        ending = msgtime+"Joined Server: "+server.name+" ("+str(server.id)+")"
        begin = "=====================================\n"
        logging.info(ending)
        await self.bot.send_message(log_channel, "```{}```".format(ending))
        pass

    async def on_server_remove(self, server):
        log_channel = self.bot.get_server("107883969424396288").get_channel("257926036728184832")
        error_channel = self.bot.get_server("107883969424396288").get_channel("257922447205072897")
        await self.bot.wait_until_ready()
        localtime = time.localtime()
        tm_mon = localtime.tm_mon
        tm_min = localtime.tm_min
        tm_mday = localtime.tm_mday
        tm_hour = localtime.tm_hour
        if localtime.tm_hour >= 13:
            hourmin = localtime.tm_hour - 12
            hourmin = str(hourmin)+":"+str(localtime.tm_min)+" PM"
        else:
            hourmin = str(localtime.tm_hour)+":"+str(localtime.tm_min)+" AM"
        msgtime = "[ "+"{0}/{1}/16 | {2} ".format(tm_mon,tm_mday,hourmin)+" ]\n"
        ending = msgtime+"Left Server: "+server.name+" ("+str(server.id)+")"
        begin = "=====================================\n"
        logging.info(ending)
        await self.bot.send_message(log_channel, "```{}```".format(ending))
        pass

    async def on_message(self, message):
        bot = self.bot
        log_channel = bot.get_server("107883969424396288").get_channel("257926036728184832")
        error_channel = bot.get_server("107883969424396288").get_channel("257922447205072897")
        # general values
        server = message.server

        msgtime = datetime.datetime.now().strftime("""%b %d, %Y at %I:%M %p (%H:%M)""")

        if not message.channel.is_private: #If the channel is not private
            fille = "./data/config/servers/"+server.id+"/server_settings.ini"
            if not os.path.isfile(fille):
                moderation.create_server_ini(message.server, True)
            try:
                booleann = moderation.get_value(fille, 'settings', 'log')
            except:
                print(server.name+" "+server.id)

            # if the server id is in the server list, then log the message to the server file
            if booleann.lower() == 'true':
                serverfp = './logs/servers/{}'.format(server.name)
                if os.path.exists(serverfp) == False:
                    os.makedirs(serverfp)
                if not os.path.isfile(serverfp+"/{}.txt".format(message.channel.name)):
                    f = open(serverfp+"/{}.txt".format(message.channel.name), 'w')
                    f.close()
                text = msgtime+" {}: {}".format(message.author.name+'#'+message.author.discriminator, message.content)
                f = open('./logs/servers/{}/{}.txt'.format(server.name, message.channel.name),'a', encoding='utf-8')
                f.write(text+'\n')
                f.close()

        if not message.channel.is_private:
            fp = ("./data/config/servers/"+message.server.id+"/server_settings.ini")
            boolean = moderation.get_value(fp, 'settings', 'ignore').lower()
        if (not message.channel.is_private and ((boolean == 'false' or message.content.startswith(bot.command_prefix[0]+'settings')) or (message.author == message.server.me))): #Check if server config's ignore is true and if so run command
            try:
                await self.process_commands(message)
            except:
                raise
            else:
                for x in range(len(bot.command_prefix)):
                    if message.author != message.server.me and message.content.startswith(bot.command_prefix[x]):
                        begin = "==============================\n"
                        time = datetime.datetime.now().strftime("""%b %d, %Y at %I:%M %p (%H:%M)""")+"\n"
                        ending = "\"{0.content}\" was issued by \"{0.author.name}#{0.author.discriminator}\" on \"{0.server.name}\"({0.channel.name})".format(message)
                        logging.info(ending)
                        await bot.send_message(log_channel, "```{}```".format(time+ending))
        elif message.channel.is_private:
            await self.process_commands(message)
            pass
        else:
            pass

    async def on_error(self, exception, context):
        with open("./logs/error2.log", "a") as f:
            traceback.print_exception(type(exception), exception, exception.__traceback__, file=f)
        pass

def setup(bot):
    n = events(bot)
    bot.add_cog(n)