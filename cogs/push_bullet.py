import asyncio
import discord
from discord.ext import commands
import cogs.utils.checks as checks
from pushbullet import Pushbullet
import configparser
import datetime

global config
config = configparser.ConfigParser()
config.read('./data/config/config.ini')

class push_bullet:
    """Random Commands"""
    def __init__(self, bot):
        self.bot = bot
        self.pb = Pushbullet(config['push']['id'])

    async def on_message(self, message):
        if not message.channel.is_private and message.server.me.mentioned_in(message) and not message.author.bot and message.author != message.server.me: #Send push update if I am Mentioned
            me_mentioned = datetime.datetime.now().strftime("""%b %d, %Y at %I:%M %p (%H:%M)""")+"\nI have been mentioned in '"+message.channel.name+"' on '"+message.server.name+"' by '"+message.author.name+"#"+message.author.discriminator+"'\nMessage: "+message.content
            print("==============================\n"+me_mentioned)
            push = self.pb.push_note('Discord Mention', me_mentioned+"\nhttps://discordapp.com/channels/"+str(message.server.id)+"/"+str(message.channel.id))

def setup(bot):
    n = push_bullet(bot)
    bot.add_cog(n)