# -*- coding: utf-8 -*-
import asyncio
import discord
from discord.ext import commands
import os
import datetime
import configparser
import subprocess
import sys
import cogs.moderation as moderation
import logging

current_game = None

config = configparser.ConfigParser()
config.read('./data/config/config.ini')

command_prefix = (config["bot"]["prefix"]+",c.").split(',')
disc = config["bot"]["disc"]

bot = commands.Bot(command_prefix=command_prefix, description=disc, pm_help=True, self_bot=True)


cogs = [f for f in os.listdir("./cogs") if os.path.isfile(os.path.join("./cogs", f))]

#log = logging.basicConfig(format="[%(asctime)s][%(levelname)s]: %(message)s", level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p')
#handler = logging.FileHandler()
#handler.setFormatter(logging.Formatter(fmt="[%(asctime)s][%(levelname)s]: %(message)s", datefmt='%m/%d/%Y %I:%M:%S %p'))

log = logging.getLogger('discord')
log.setLevel(logging.INFO)
handler = logging.FileHandler(filename='./logs/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(fmt="[%(asctime)s][%(levelname)s]: %(message)s", datefmt='%m/%d/%Y %I:%M:%S %p'))
log.addHandler(handler)
log.setLevel(logging.INFO)

@bot.event
@asyncio.coroutine
def on_ready():
    subprocess.call('clear',shell=True)
    logging.info('Successfully Logged in!')
    logging.info('Starting cogs...')
    loaded_cogs = []
    for cog in cogs:
        cog = cog.replace('.py','')
        try:
            bot.load_extension('cogs.'+cog)
            logging.info('Loaded cog: '+cog)
            loaded_cogs.append(cog)
        except Exception as e:
            logging.info('Couldn\'t load cog: '+cog)
            print('\tError: {}'.format(type(e).__name__, e))
            #raise
        yield from asyncio.sleep(0.1)
    loaded_cogs_str =  str(', ').join(list(loaded_cogs))
    logging.info('Cogs Finished loading!!')
    yield from asyncio.sleep(1)
    subprocess.call('clear',shell=True)
    whitelisted_servers = []
    for channel in list(bot.get_all_channels()):
        fp = ("./data/config/servers/"+channel.server.id+"/server_settings.ini")
        boolean = moderation.get_value(fp, 'settings', 'ignore').lower()
        if boolean == 'false' and str(channel.server.name) not in whitelisted_servers:
            whitelisted_servers.append(channel.server.name)
    print('------\nCurrently logged in as ['+bot.user.name+' (ID: "'+bot.user.id+'")]')
    print('Number of Servers Connected: '+str(len(list(bot.servers)))+'\nNumbers of DMs: '+str(len(list(bot.private_channels))))
    print('Current Prefixes: '+", ".join(bot.command_prefix))
    print('------\nCurrently loaded cogs: ({0} out of {1})\n'.format(str(len(loaded_cogs)),str(len(cogs)))+loaded_cogs_str)
    print('------\nCurrently Whitelisted Servers: ('+str(len(whitelisted_servers))+' out of '+str(len(list(bot.servers)))+')\n'+', '.join(whitelisted_servers)+"\n------")
    try:
        f = open("data/game.txt", 'r')
        current_game = f.read()
        f.close()
    except:
        f = open("data/game.txt", 'w')
        f.close()
        current_game = None
    if current_game == '':
        game = None
    else:
        game = discord.Game(name=current_game)
    yield from bot.change_presence(game=game, status=discord.Status.invisible)
    log.setLevel(logging.INFO)

@bot.event
async def on_message(message):
    pass

email = config.get('bot','email')
password = config.get('bot','password')
token = config.get('bot','token')

if config.getboolean('bot','use_token') == False:
    bot.run(email, password)
else:
    bot.run(token)