import asyncio
import discord
from discord.ext import commands
import cogs.utils.checks as checks
import praw
import datetime
import time
import math
from PIL import Image
import requests
from io import BytesIO
import random
import os
from time import sleep
import pyperclip
from cleverbot import Cleverbot
import configparser
from dateutil.relativedelta import relativedelta
import binascii
import youtube_dl
import re
from xml.etree import ElementTree
import html
import lxml.html as hxml
import traceback
import json
from cogs.utils.vndb import VNDB
import arrow
from zipfile import ZipFile
import subprocess

from io import BytesIO
from io import TextIOWrapper
from PIL import Image

global config
config = configparser.ConfigParser()
config.read('./data/config/config.ini')

class general:
    """General Commands"""
    def __init__(self, bot):
        self.reddit = praw.Reddit(client_id=config["praw"]["client_id"], client_secret=config["praw"]["client_secret"], user_agent=config["praw"]["user_agent"],username=config["praw"]["user"], password=config["praw"]["pass"])
        self.bot = bot
        self.cb = Cleverbot()

    @commands.command(name='emoji')
    @checks.is_owner()
    @asyncio.coroutine
    def _emoji_big(self, emoji : discord.Emoji = None):
        """Makes any custom emoji big :D (Doesn't work with stock emojis)"""
        if emoji == None:
            yield from self.bot.say('***No emojis/emotes!*** :FeelsBadManHD:')
            return
        else:
            yield from self.bot.say('{0.url}'.format(emoji))
        pass

    @commands.command(name='info', pass_context=True, no_pm=True)
    async def _get_member_info(self, ctx, *, member : discord.Member = None):
        """Get Info for a user"""
        if member == None:
            member = ctx.message.author
        online = str(member.status).title()
        if member.created_at:
            created_at = "{}".format(member.created_at.strftime("%d %b %Y %H:%M"))
            created = member.created_at
            arrow_created_at = arrow.utcnow().fromdatetime(created).humanize().title()
        else:
            created_at = "<ERROR>"
            created = None
            arrow_created_at = "<ERROR>"
        if member.joined_at:
            joined_at = "{}".format(member.joined_at.strftime("%d %b %Y %H:%M"))
            joined = member.joined_at
            arrow_joined_at = arrow.utcnow().fromdatetime(joined).humanize().title()
        else:
            joined_at = "<ERROR>"
            joined = None
            arrow_joined_at = "<ERROR>"
        roles = member.roles
        if len(roles) > 1:
            roles = roles[1:]
            roles = ", ".join([role.name for role in roles])
        else:
            roles = "<no roles>".upper()
        if member.color:
            data = discord.Embed(colour=member.colour)
        data.add_field(name="Created On:", value=created_at, inline=True)
        data.add_field(name="Joined On:", value=joined_at, inline=True)
        data.add_field(name="Created Span:", value=arrow_created_at, inline=True)
        data.add_field(name="Joined Span:", value=arrow_joined_at, inline=True)
        data.add_field(name="Status:", value=online, inline=True)
        if member.top_role.name == "@everyone":
            top_role = "<no top role>".upper()
        else:
            top_role = member.top_role.name
        data.add_field(name="Top Role:", value=top_role, inline=True)
        data.add_field(name="Roles:", value=roles, inline=False)
        extra = ""
        if member != ctx.message.author:
            extra = " | Issued By: {0.name}#{0.discriminator}".format(ctx.message.author)
        data.set_footer(text="User ID: " + member.id + extra)
        if member.avatar_url != "":
            avatar_url = member.avatar_url
        else:
            avatar_url = member.default_avatar_url
        extra_name = ""
        if member.display_name != member.name:
            extra_name = " ({})".format(member.display_name)
        data.set_author(name=member.name+"#"+member.discriminator+extra_name, url=avatar_url, icon_url=avatar_url)
        data.set_thumbnail(url=avatar_url)
        try:
            await self.bot.say(embed=data)
        except discord.HTTPException:
            raise

    @commands.command(name='oldinfo', pass_context=True, hidden=True, no_pm=True)
    async def _get_member_info_old(self, ctx, *, member : discord.Member = None):
        await self.bot.type()
        if member == None:
            member = ctx.message.author
        code_block_beginning = "```md\n"
        code_block_ending = "```"
        name_plus_num = member.name+'#'+str(member.discriminator)
        memid = member.id

        if member.display_name != member.name:
            display_name = '[Display Name]:        {}\n'.format(member.display_name)
        else:
            display_name = ''

        if member.game == None:
            if str(member.status) == 'online' or str(member.status) == 'idle':
                game = "Not Playing Anything"
            else:
                game = "Offline"
        else:
            game = "Playing "+member.game.name
        colorhex = str(hex(member.color.value))[2:]
        if member.avatar_url == '':
            avatar = member.default_avatar_url
        else:
            avatar = member.avatar_url


        today = datetime.datetime.now()

        joined = member.joined_at
        day = joined.day
        month = joined.month
        months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        text_mon = months[month-1]
        year = joined.year

        hour = joined.hour
        am = "AM"
        if hour > 12:
            hour-=12
            am = "PM"
        time = "{}:{} {}".format(hour,joined.minute,am)

        joineddate = joined.strftime("""%A, %B %d, %Y at %I:%M %p (%H:%M)""")
        #joineddate = "{} {}, {} at {} EST".format(text_mon, str(day).zfill(2), str(year).zfill(4), time)
        #date_ago = joined - today
        date_ago = relativedelta(today, joined)
        ago = ""
        if date_ago.hours >= 2:
            ago = "{} minutes, ".format(date_ago.minutes)
        elif date_ago.hours == 1:
            ago = "{} minute, ".format(date_ago.minutes)

        if date_ago.hours >= 2:
            ago = "{} hours, ".format(date_ago.hours)+ago
        elif date_ago.hours == 1:
            ago = "{} hour, ".format(date_ago.hours)+ago

        if date_ago.days >= 2:
            ago = "{} days, ".format(date_ago.days)+ago
        elif date_ago.days >= 2:
            ago = "{} day, ".format(date_ago.days)+ago

        if date_ago.months >= 2:
            ago = "{} months, ".format(date_ago.months)+ago
        elif date_ago.months == 1:
            ago = "{} month, ".format(date_ago.months)+ago

        if date_ago.years >= 2:
            ago = "{} years, ".format(abs(date_ago.years))+ago
        elif date_ago.years == 1:
            ago = "{} year, ".format(abs(date_ago.years))+ago

        ago = ago[:-2]+" ago"

        message = code_block_beginning+"[Name]:                {}\n{}[ID]:                  {}\n[Joined On]:           {} [{}]\n[Status]:              {}\n[Color/Colour]:        #{}".format(name_plus_num, display_name, memid, joineddate, ago, game, colorhex)+code_block_ending

        await self.bot.say(message+avatar)

    @commands.command(name="binary", pass_context=True, hidden=True)
    @asyncio.coroutine
    def convert_binary(self, ctx, to_from = None, *, binary = None):
        if to_from == "from":
            n = int('0b'+binary, 2)
            text = n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()
            yield from self.bot.say(text)
        elif to_from == "to":
            n = bin(int.from_bytes(binary.encode(), 'big'))
            text = n[2:]
            text = "0"+text
            yield from self.bot.say(text)
        else:
            yield from self.bot.say('Error!! Please type either `to` or `from` after the command!!')
        pass

    @commands.command(name="joined", pass_context=True)
    @asyncio.coroutine
    def _memeber_joined(self, ctx, *, member : discord.Member = None):
        """Shows the joined date and time for the mentioned user"""
        if member == None:
            member = ctx.message.author
        joined = member.joined_at
        joined_str = joined.strftime("%b %d, %Y %I:%M %p (%H:%M)")
        ago = relativedelta(datetime.datetime.today(), joined)
        ago_str = "{0.days} days ago, {0.hours} hours ago, and {0.minutes} minutes ago".format(ago)
        embed = discord.Embed(colour=member.colour)
        embed.add_field(name="Joined On:", value=joined_str+"\n"+ago_str)
        yield from self.bot.say(embed=embed)

    @commands.command(name="oldjoined", pass_context=True, hidden=True)
    @asyncio.coroutine
    def _memeber_joined_old(self, ctx, *, member : discord.Member = None):
        if member == None:
            member = ctx.message.author
        today = datetime.datetime.now()
        joined = member.joined_at
        day = joined.day
        month = joined.month
        months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        text_mon = months[month-1]
        year = joined.year

        hour = joined.hour
        am = "AM"
        if hour > 12:
            hour-=12
            am = "PM"
        time = "{}:{} {}".format(hour,joined.minute,am)

        joineddate = "{} {}, {} at {} EST".format(text_mon, str(day).zfill(2), str(year).zfill(4), time)
        date_ago = relativedelta(today, joined)
        ago = ""
        if date_ago.hours >= 2:
            ago = "{} minutes, ".format(date_ago.minutes)
        elif date_ago.hours == 1:
            ago = "{} minute, ".format(date_ago.minutes)

        if date_ago.hours >= 2:
            ago = "{} hours, ".format(date_ago.hours)+ago
        elif date_ago.hours == 1:
            ago = "{} hour, ".format(date_ago.hours)+ago

        if date_ago.days >= 2:
            ago = "{} days, ".format(date_ago.days)+ago
        elif date_ago.days >= 2:
            ago = "{} day, ".format(date_ago.days)+ago

        if date_ago.months >= 2:
            ago = "{} months, ".format(date_ago.months)+ago
        elif date_ago.months == 1:
            ago = "{} month, ".format(date_ago.months)+ago

        if date_ago.years >= 2:
            ago = "{} years, ".format(abs(date_ago.years))+ago
        elif date_ago.years == 1:
            ago = "{} year, ".format(abs(date_ago.years))+ago

        ago = ago[:-2]+" ago"

        yield from self.bot.say("```md\n[{} Joined On]: {}\n[Joined]: {}```".format(member.display_name, joineddate, ago))

    @commands.command(name='hug', aliases=['hugs'], pass_context=True)
    async def _hug_member(self, ctx, *, member : discord.Member = None):
        """Hugs said member | Mention or Type the name (case-sensitive/spaces )"""
        if member == None:
            mention = ''
        elif member == ctx.message.server.me and ctx.message.author.id != '130760764893036544' and ctx.message.author != ctx.message.server.me:
            await self.bot.say('***Error:*** *I can\'t hug myself silly.*')
            return
        elif member == ctx.message.author and member != ctx.message.server.me:
            await self.bot.say('***Error:*** *You\'re trying to hug yourself. Do you not have friends?*')
            return
        else:
            mention = ' '+member.mention
        files = [f for f in os.listdir(os.path.abspath("./data/hugs")) if os.path.isfile(os.path.join(os.path.abspath("./data/hugs"), f))]
        rannum = random.randrange(len(files))
        await self.bot.type()
        try:
            await self.bot.send_file(ctx.message.channel, os.path.abspath("./data/hugs")+"/"+files[rannum], content='*hugs'+mention+'*')
        except discord.errors.HTTPException:
            rannum = random.randrange(len(files))
            await self.bot.send_file(ctx.message.channel, os.path.abspath("./data/hugs")+"/"+files[rannum], content='*hugs'+mention+'*')
        except:
            pass
        pass

    @commands.command(pass_context=True)
    async def lenny(self, ctx):
        '''Posts a lenny face: ( ͡° ͜ʖ ͡°)'''
        if ctx.message.author == ctx.message.server.me:
            await self.bot.edit_message(ctx.message, '( ͡° ͜ʖ ͡°)')
        else:
            await self.bot.say('( ͡° ͜ʖ ͡°)')

    @commands.command(pass_context=True)
    async def really(self, ctx):
        '''Posts this face: ಠ_ಠ'''
        if ctx.message.author == ctx.message.server.me:
            await self.bot.edit_message(ctx.message, 'ಠ_ಠ')
        else:
            await self.bot.say('ಠ_ಠ')

    @commands.command(pass_context=True, aliases=['shrugu'])
    async def shrug(self, ctx):
        '''Posts shrug: ¯\_(ツ)_/¯'''
        if ctx.message.author == ctx.message.server.me:
            await self.bot.edit_message(ctx.message, '¯\_(ツ)_/¯')
        else:
            await self.bot.say('¯\_(ツ)_/¯')

    @commands.command(name="cowsay", hidden=True, aliases=["say"], pass_context=True)
    @asyncio.coroutine
    def send_cow_say(self, ctx, *, text : str = "The Command issuer is a dum dum! >3>"):
        output = subprocess.run("echo \"{}\"|/usr/games/cowsay".format(text), shell=True, stdout=subprocess.PIPE).stdout
        yield from self.bot.say("```{}```".format(output.decode("utf-8")))
        yield from asyncio.sleep(0.1)
        yield from self.bot.delete_message(ctx.message)
        pass

    @commands.command(aliases=['ava'],pass_context=True)
    async def avatar(self, ctx, *, member : discord.Member = None):
        """Show Avatar of the user | Mention or Type the name (case-sensitive/spaces allowed)"""
        if member == None:
            member = ctx.message.author
        data = discord.Embed(colour=member.colour)
        if member != ctx.message.author:
            data.set_footer(text="Issued By: {0.name}#{0.discriminator}".format(ctx.message.author))
        if member.avatar_url != "":
            avatar_url = member.avatar_url
        else:
            avatar_url = member.default_avatar_url
        extra_name = ""
        if member.display_name != member.name:
            extra_name = " ({})".format(member.display_name)
        data.set_author(name=member.name+"#"+member.discriminator+extra_name, url=avatar_url)
        data.set_image(url=avatar_url)
        try:
            await self.bot.say(embed=data)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission to send this")

    @commands.command(name="oldava",pass_context=True, hidden=True)
    async def avatar_old(self, ctx, *, user : discord.Member = None):
        if user == None:
            user = ctx.message.author
        await self.bot.say(user.avatar_url)
        pass

    @commands.command(aliases=["ver"], hidden=True)
    async def version(self):
        await self.bot.say('**Discord Version:** `'+discord.__version__+'` **Discord.py Version:** `'+'v0.10.0'+'`')

    @commands.command(pass_context=True, aliases=['c'], hidden=True)
    @checks.is_owner()
    async def cow(self, ctx, type = 'aii'):
        await self.bot.upload('data/cow/cow'+type+'.png')
        sleep(2)
        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True, aliases=['f'], name='file', hidden=True)
    @checks.is_owner()
    async def _file(self, ctx, *, location : str):
        #if checks.check_permissions(ctx, attach_files=True):
        try:
            await self.bot.upload('data/'+location)
            sleep(2)
            await self.bot.delete_message(ctx.message)
        except FileNotFoundError:
            await self.bot.say('`Can\'t Find the file: \''+location+'\'`')
            sleep(2)
            await self.bot.delete_message(ctx.message)
        except:
            await self.bot.say('`An error showed up`')
            sleep(2)
            await self.bot.delete_message(ctx.message)
            raise

    @commands.command(aliases=['pets','pat','pet'], pass_context=True)
    async def pats(self, ctx, *, user : discord.Member = None):
        """Pats a user | Either mention the user or type their name (case-sensitive/spaces allowed)"""
        if user != None:
            user = user.mention+' '
        else:
            user = ''
        msg = await self.bot.say("***Loading...***")
        hp = self.reddit.subreddit('headpats')
        thing = hp.random()
        link = thing.url
        await self.bot.delete_message(msg)
        if ctx.message.mentions: 
            await self.bot.say(user+link)
        else:
            await self.bot.say(link)

    @commands.command(aliases=['moos'], pass_context=True)
    async def moo(self, ctx, *, user : discord.Member = None):
        """Sends a random post from the /r/cow subreddit"""
        if user == None:
            user = ''
        else:
            user = user.mention+' '
        msg = await self.bot.say("***Loading...***")
        hp = self.reddit.subreddit('cow')
        thing = hp.random()
        link = thing.url
        await self.bot.edit_message(msg, user+link)

    @commands.command(aliases=['pong'], pass_context=True)
    @commands.cooldown(5, 10, commands.BucketType.user)
    async def ping(self, ctx):
        """Sends Pong and time it took in ms to send"""
        color = discord.Colour.default()
        if not ctx.message.channel.is_private:
            color = ctx.message.author.colour
        t1 = time.perf_counter()
        await self.bot.type()
        t2 = time.perf_counter()
        embed = discord.Embed(title="Pong!", description="{0}ms".format(round((t2-t1)*1000)), colour=discord.Colour(value=ctx.message.author.colour.value))
        if ctx.message.author != ctx.message.server.me:
            embed.set_footer(text="Issued by: {0.name}#{0.discriminator}".format(ctx.message.author))
        await self.bot.say(embed=embed)
        #await self.bot.say("```md\n[Pong]: {}ms```".format(round((t2-t1)*1000)))

    @commands.command(pass_context=True)
    @commands.cooldown(2, 10)
    async def serverinfo(self, ctx):
        """Shows server's information"""
        server = ctx.message.server
        online = len([m.status for m in server.members if m.status == discord.Status.online or m.status == discord.Status.idle])
        total_users = len(server.members)
        text_channels = len([x for x in server.channels if x.type == discord.ChannelType.text])
        voice_channels = len(server.channels) - text_channels
        passed = (ctx.message.timestamp - server.created_at).days
        created_at = ("Since {}. That's over {} days ago!".format(server.created_at.strftime("%d %b %Y %H:%M"), passed))
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        data = discord.Embed(description=created_at, colour=discord.Colour(value=colour))
        data.add_field(name="Region", value=str(server.region))
        data.add_field(name="Users", value="{} Online/{} Total".format(online, total_users))
        data.add_field(name="Text Channels", value=text_channels)
        data.add_field(name="Voice Channels", value=voice_channels)
        data.add_field(name="Roles", value=len(server.roles))
        data.add_field(name="Owner", value=str(server.owner))
        data.set_footer(text="Server ID: " + server.id)

        if server.icon_url:
            data.set_author(name=server.name, url=server.icon_url)
            data.set_thumbnail(url=server.icon_url)
        else:
            data.set_author(name=server.name)

        try:
            await self.bot.say(embed=data)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission to send this")

    @commands.command(pass_context=True, name='oldserverinfo', hidden=True)
    @commands.cooldown(2, 10)
    async def serverinfo_old(self, ctx, *, server : discord.Server = None):
        if server == None:
            server = ctx.message.server
        name = str(server.name)
        date_created = server.created_at
        default_channel = server.default_channel.name
        region = str(server.region)
        if server.owner.name != server.owner.display_name:
            owner = "{}#{} ({})".format(server.owner.name, server.owner.discriminator, server.owner.display_name)
        else:
            owner = "{}#{}".format(server.owner.name, server.owner.discriminator)
        membercount = server.member_count
        channels = ', '.join(channel.name for channel in server.channels)
        serverid = server.id
        icon = server.icon_url
        msg = '```md\n[Server Name]: '+name+'\n[Date Made]: '+'{0}/{1}/{2}'.format(date_created.month, date_created.day, date_created.year)+'\n[Region]: '+str(region)+'\n[Owner]: '+owner+'\n[Member Count]: '+str(membercount)+' Members```'
        await self.bot.say(msg)

    @commands.command(pass_context=True, name='guessname', aliases=['guess'], enabled=False, hidden=True)
    async def guess_name(self, ctx, name):
        api_url = 'https://montanaflynn-gender-guesser.p.mashape.com/?name='
        headers={
          "X-Mashape-Key": "bYuPeQ27Prmsha9bRRD6LwkGrU45p15Zt91jsnitgSghjKvZ58",
          "Accept": "application/json",
          'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
        }
        url = api_url+name
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            try:
                await self.bot.say("```Name: "+name+"\nError: "+r.json()['error']+"```")
            except:
                gender = r.json()['gender']
                desc = r.json()['description']
                await self.bot.say("```Name: "+name+"\nGender: "+gender+"\nAssumption: "+desc+"```")
        else:
            await self.bot.say('Error: `Status Code: '+str(r.status_code)+'`')
            sleep(3)
            await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True, name='randu', aliases=['randomuser','ranuser'])
    @commands.cooldown(2, 30, commands.BucketType.user)
    async def random_member(self, ctx):
        """Gets a random user from the current server"""
        thing = random.randint(0, len(ctx.message.server.members)-1)
        members = list(ctx.message.server.members)
        member = members[thing]
        await self.bot.say('Random Member: `'+str(member.name)+'`')
    
    @commands.command(pass_context=True, name='membercount', aliases=['getmembers'])
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def get_member_amount(self, ctx):
        """Shows the amount of Member in the current server"""
        if ctx.message.channel.is_private:
            await self.bot.say(":neutral_face: Really?")
            sleep(3)
            await self.bot.delete_message(ctx.message)
            return
        await self.bot.say("`Number of Members: "+str(ctx.message.server.member_count)+"`")
        sleep(3)
        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True, name='convert', hidden=True)
    async def _convert_F_C(self, ctx, *, temp : str):
        if temp.endswith('C') or temp.endswith('c'):
            from_cel = True
        elif temp.endswith('F') or temp.endswith('f'):
            from_cel = False
        else:
            return
        if from_cel:
            tempnum = temp.replace('C','')
            tempnum = tempnum.replace('c','')
            tempnum = float(tempnum)
            finalnum = tempnum * 1.8000
            finalnum = finalnum + 32.00
            await self.bot.say(temp+'<==>'+str("{0:.2f}".format(round(finalnum,2)))+'F')
        elif not from_cel:
            tempnum = temp.replace('F','')
            tempnum = tempnum.replace('f','')
            tempnum = float(tempnum)
            finalnum = tempnum - 32.00
            finalnum = finalnum / 1.80000
            await self.bot.say(temp+'<==>'+str("{0:.2f}".format(round(finalnum,2)))+'C')

    @commands.command(pass_context=True, name='remindme', hidden=True)
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def remindme(self, ctx, time = 0, *, msg = "Time's up!"):
        if time == 0:
            return
        member = ctx.message.author
        await self.bot.say("{0}: Remind Set! I will mention you and send \"{1}\" within this channel when time is over!".format(member.display_name, msg))
        await asyncio.sleep(time)
        await self.bot.say("{0}: {1}".format(member.mention, msg))
        pass

    @commands.command(pass_context=True, name="ytdl", aliases=['downloadyt', 'dlyt', "dl", "download"])
    @commands.cooldown(2, 10, commands.BucketType.server)
    async def download_youtube_video_into_mp3(self, ctx, *, links : str):
        """Downloads and converts youtube video(s), then uploads said video(s)"""
        if not links.startswith("http"):
            await self.bot.say("*`Please Start with a HTTP URL!`*")
            return
        links = links.split(" ")
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        if len(links) > 1 and (not links[1].startswith("-") or len(links) != 2):
            embed = discord.Embed(title="Multiple Youtube Download... [{} Total]".format(len([link for link in links])), description="*All done by Youtube-DL*")
            embed_msg = await self.bot.say(embed=embed)
            before = datetime.datetime.now()
            x = 0
            fp = "/media/seacow/Music/{}.zip".format("Songs_for_"+ctx.message.author.name.replace(" ", "_"))
            zips = ZipFile(fp, "w")
            while x < len(links):
                dont_convert = False
                dont_upload = False
                if "-noconvert" in links[x]:
                    del links[x]
                    dont_convert = True
                    x = x - 1
                elif "-noupload" in links[x]:
                    del links[x]
                    x = x - 1
                link = links[x]
                afterdl = await self.download_video_song(link, dont_convert = dont_convert, dont_upload = dont_upload, multi=True, embed=embed, embed_msg=embed_msg)
                z = afterdl[1]
                if z != None:
                    zips.write(z, arcname=z.split("/")[-1])
                x += 1
            zips.close()
            after = datetime.datetime.now()
            elapsed = after - before
            embed = afterdl[0]
            embed.add_field(name="Downloads Complete! Uploading...", value="*Took {0.seconds} seconds*".format(elapsed), inline=False)
            await self.bot.edit_message(embed_msg, embed=embed)
            await self.bot.upload(fp)
            os.remove(fp)
            embed.set_field_at(-1, name="Upload Complete!", value=embed.fields[-1].value, inline=embed.fields[-1].inline)
            await self.bot.edit_message(embed_msg, embed=embed)
        else:
            links = " ".join(links)
            dont_convert = False
            dont_upload = False
            if "-noconvert" in links:
                dont_convert = True
            elif "-noupload" in links:
                dont_upload = True
            link = links.split(" ")[0]
            await self.download_video_song(link = link, dont_convert = dont_convert, dont_upload = dont_upload)

    async def download_video_song(self, link, dont_convert = False, dont_upload = False, multi=False, embed=None, embed_msg=None):
        if not dont_convert and not multi:
            #ytdl_msg = await self.bot.say("*Starting Download and Conversion!*")
            embed = discord.Embed(title="Youtube Download/Conversion...", description="*Download and Conversion done by Youtube-DL*", url=link)
        elif dont_convert and not multi:
            #ytdl_msg = await self.bot.say("*Starting Download! (Don't Convert)*")
            embed = discord.Embed(title="Youtube Download...", description="*Download done by Youtube-DL*", url=link)
        else:
            ytdl_msg = embed_msg

        ydl_opts = {
            "quiet":True,
            'noplaylist':True,
            'nooverwrites':True,
            'nocolor':True,
            'format': 'bestaudio/best',
            'outtmpl':'/media/seacow/Music/%s.%s' % ('%(id)s', '%(ext)s'),
        }
        convert_list = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            },{
                'key': 'MetadataFromTitle',
                'titleformat': '%s - %s [%s]' % ('%(artist)s', '%(track)s', '%(album)s'),
            },{
                'key':'FFmpegMetadata',
            },{
                'key':'XAttrMetadata',
            }]
        if not dont_convert:
            ydl_opts["postprocessors"] = convert_list

        yt = youtube_dl.YoutubeDL(ydl_opts)
        info = yt.extract_info(link, download=False)
        duration = info["duration"]
        dur_min = int(duration / 60)
        dur_sec = duration - (60 * dur_min)
        dur = "{0}:{1}".format(dur_min, dur_sec)
        title = info["title"] if info["title"] else info["alt_title"]
        extra = ""
        if not multi:
            embed.add_field(name="Video: [{}]".format(dur), value=title)
            embed.add_field(name="Uploader:", value=info["uploader"])
            ud = info["upload_date"]
            try:
                upload_date = datetime.datetime.strptime(ud, "%Y%m%d").strftime("%B %d, %Y")
            except:
                upload_date = ud
            embed.add_field(name="Date Uploaded:", value=upload_date)
            embed.add_field(name="Rating:", value=str(info["average_rating"])[:4])
            #embed.add_field(name="Duration:", value=dur)
            embed.set_thumbnail(url=info["thumbnail"])
            embed.add_field(name="Progress:", value="*Starting Download...*", inline=False)
            ytdl_msg = await self.bot.say(embed=embed)
        else:
            ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])
            extra = "[Link]({}) ".format(link)
            embed.add_field(name="{} Video: {} [{}]".format(ordinal(len(embed.fields)+1), title, dur), value=extra+"*Starting Download...*", inline=True)
            await self.bot.edit_message(ytdl_msg, embed=embed)

        if duration >= 420 and not info["is_live"]:
            embed.set_field_at(-1, name=embed.fields[-1].name, value=extra+"<ERROR>: *Video is too long (7 minute limit)*", inline=embed.fields[-1].inline)
            ytdl_msg = await self.bot.edit_message(ytdl_msg, embed=embed)
            return
        if info["is_live"]:
            embed.set_field_at(-1, name=embed.fields[-1].name, value=extra+"<ERROR>: *You can't download a live video...*", inline=embed.fields[-1].inline)
            ytdl_msg = await self.bot.edit_message(ytdl_msg, embed=embed)
            return
        yt.download([link])
        if not dont_upload and not multi:
            embed.set_field_at(-1, name=embed.fields[-1].name, value=extra+"*Download Complete! Uploading...*", inline=embed.fields[-1].inline)
            await self.bot.edit_message(ytdl_msg, embed=embed)
        try:
            z = None
            fp = "/media/seacow/Music/{}.mp3".format(info["id"])
            if not dont_convert and not dont_upload and not multi:
                await self.bot.upload(fp)
            elif dont_convert or dont_upload:
                pass
            elif multi:
                #TODO: Upload zip
                z = fp
                pass
        except:
            embed.set_field_at(-1, name=embed.fields[-1].name, value="<ERROR>: *Couldn't Upload :\*", inline=embed.fields[-1].inline)
            await self.bot.edit_message(ytdl_msg, embed=embed)
        else:
            if not dont_convert and not dont_upload and not multi:
                embed.set_field_at(-1, name=embed.fields[-1].name, value="*Upload Complete!*", inline=embed.fields[-1].inline)
            elif dont_convert or dont_upload or multi:
                embed.set_field_at(-1, name=embed.fields[-1].name, value=extra+"*Download Complete!*", inline=embed.fields[-1].inline)
            await self.bot.edit_message(ytdl_msg, embed=embed)
        return [embed, z]

    @commands.command(hidden=True, pass_context=True)
    @commands.cooldown(5, 10, commands.BucketType.user)
    async def takeoverserveranddontletvenikwin(self, ctx):
        if ctx.message.server.id == "234643592528789505":
            await self.bot.say("***COMMENCING REMOVAL OF {}***".format(ctx.message.server.get_member("234261693738254336").mention))
        pass

    @commands.command(hidden=True, pass_context=True)
    async def neku(self, ctx):
        data = discord.Embed(title="Neku's Website", url="https://nekku.me/", description="A man searching for perfection, hoping to satisfy himself.", timestamp=datetime.datetime.utcnow())
        data.set_author(name="{0.name}#{0.discriminator}".format(ctx.message.server.get_member("130760764893036544")), icon_url=ctx.message.server.get_member("130760764893036544").avatar_url)
        data.set_thumbnail(url="https://www.nekku.me/images/favicon.gif")

        try:
            await self.bot.say(embed=data)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission to send this")
        pass

    @commands.command(hidden=True, pass_context=True)
    @checks.is_owner()
    async def test(self, ctx):
        msg = ctx.message
        #url = msg.author.avatar_url
        #url = url.replace("https", "http")
        #temp = "./temp/{0}.{1}".format(, )
        #thing = requests.get(ctx.message.author.avatar_url)
        #import urllib.request as r
        #f = r.urlretrieve(url, filename=url.split("/")[-1])
        #f = open(f, "rb")
        #await self.bot.upload(f)
        #f.close()

    @commands.command(hidden=True, pass_context=True)
    @commands.cooldown(2, 5, commands.BucketType.channel)
    async def countdown(self, ctx, time : str):
        try:
            time = int(time)
        except:
            print("ERROR: error with 'time'")
            return
        embed = discord.Embed()
        embed.set_author(name="{0.name}#{0.discriminator}".format(ctx.message.author), icon_url=ctx.message.author.avatar_url)
        embed.add_field(name="Countdown:", value="{} seconds remaining~".format(str(time)))
        msg = await self.bot.say(embed=embed)
        while time >= 0:
            time = int(time) - 1
            if int(time) == 0:
                break
            embed.set_field_at(0, name="Countdown:", value="{} seconds remaining~".format(str(time)))
            await self.bot.edit_message(msg, embed=embed)
            await asyncio.sleep(1)
        if int(time) == 0:
            embed.set_field_at(0, name="Countdown:", value="Times Up!~ {}".format(str(ctx.message.author.mention)))
            await self.bot.edit_message(msg, embed=embed)
        pass

    @commands.command(hidden=True, name="wearenumberone", aliases=["#1"])
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def command_for_datlof(self, content = None):
        if content != None and content.startswith("add"):
            content = content.split(" ")[1:]
            with open("./data/wearenumberone.json") as f:
                jsonf = json.load(f)
                for t in content:
                    if t not in jsonf["links"]:
                        jsonf["links"].append(t)
                f.write(jsonf)
            return

        with open("./data/wearenumberone.json") as f:
            links = json.load(f)
        rand = random.randrange(len(links["links"]))
        link = links["links"][rand]
        await self.bot.say(link)

    @commands.command(pass_context=True, aliases=["neko","nekomimi"])
    async def catgirl(self, ctx):
        """Posts a catgirl (Hopefully SFW) from \"http://catgirls.brussell98.tk/\""""
        page = requests.get("http://catgirls.brussell98.tk/")
        tree = hxml.fromstring(page.content)
        image = tree.xpath('//img')
        image_path = image[0].get("src")
        embed = discord.Embed(name="",description="")
        embed.set_image(url="http://catgirls.brussell98.tk{}".format(image_path))
        embed.set_footer(icon_url=ctx.message.author.avatar_url, text="{0.name}#{0.discriminator}".format(ctx.message.author))
        await self.bot.say(embed=embed)

    @commands.command(pass_context=True)
    async def translate(self, *, content):
        """Translates \"content\" into english"""
        info = {
            'q':content,
            'target': 'en',
            'format': 'text',
            'key':'AIzaSyDn36oc1lpWai8hoJhwiM2feHhNFVUcyQA'
        }
        headers = {

        }
        pass

def setup(bot):
    n = general(bot)
    bot.add_cog(n)