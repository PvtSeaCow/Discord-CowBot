import asyncio
import discord
from discord.ext import commands
import re
import requests
from urllib.parse import urlparse
import os
import datetime
from time import sleep
import cogs.utils.checks as checks
import configparser
import bitly_api
import random
from imgurpython import ImgurClient

from cogs.utils import utilities

config = configparser.ConfigParser()
serverconfig = configparser.ConfigParser()
channelconfig = configparser.ConfigParser()
config.read('./data/config/config.ini')

def urlify(s, k):
    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", k, s)
    return s

async def make_nsfw_config(path):
    tempconfig = configparser.ConfigParser()
    tempconfig.read(path)
    tempconfig["settings"] = {}
    tempconfig["channels"] = {}
    with open(path, 'w') as configfile:
        tempconfig.write(configfile)

async def download_file(url, path, file_name, file_type, disable = True):
    if disable:
        return
    if file_type == 'exe' or file_type == 'js' or file_type == 'rar' or file_type == 'com':
        return
    path = re.sub(r"[\;\:\*\"\|\>\<]", '-', path)
    if not os.path.exists('/home/seacow/Shared/'+path):
        os.makedirs('/home/seacow/Shared/'+path)
    headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
    }
    if file_name == 'unknown':
        rand = random.randint(1, 100000)
        file_name = 'unknown_'+str(rand)
    r = requests.get(url, headers=headers, stream=True)
    file_path = '/home/seacow/Shared/'+path+'/'+str(file_name)+'.'+str(file_type)
    if not os.path.isfile(file_path):
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

class nsfw:
    """Commands that are nsfw."""
    def __init__(self, bot):
        self.bot = bot
        self.waa_shorten = utilities.waa_shorten
        self.use_imgur = False
        #self.imgur = ImgurClient(config['imgur']['id'],config['imgur']['secret'])
        
    @commands.command(pass_context=True, aliases=["hentai","nsfw","lewds","loods"], help='Send nsfw images using \'content\' as tags.\nSites you can currently use: konachan, chan, ibsearch, yandere.\nSites currently being added: Danbooru, idol.\n\nExample: cow.nsfw -konachan ass\nNote: This can only be used on channels that have nsfw in the title, and only on servers I choose.', brief='''Send nsfw images using 'content' as tags.''')
    @commands.cooldown(4, 15, commands.BucketType.channel)
    async def lood(self, ctx, site : str = '-danbooru', *, content = ""):
        p = ctx.prefix
        if not ctx.message.channel.is_private:
            if ctx.message.author != ctx.message.server.me:
                serverconfig.read('./data/config/servers/'+ctx.message.server.id+'/server_settings.ini')
                if not serverconfig['settings'].getboolean('nsfw'):
                    await self.bot.say("```This server has not been configured for this command. Ask {} for help!```".format(ctx.message.server.me.display_name))
                    return
                if (os.path.isfile('./data/config/servers/'+ctx.message.server.id+'/nsfw_settings.ini') and serverconfig['settings'].getboolean('nsfw')):
                    try:
                        channelconfig.read('./data/config/servers/'+ctx.message.server.id+'/nsfw_settings.ini')
                        temp = channelconfig["channels"].getboolean(ctx.message.channel.id)
                        del temp
                    except:
                        await self.bot.say("```This channel has not been configured for this command. Ask {} for help!```".format(ctx.message.server.me.display_name))
                        return
                else:
                    await self.bot.say("```This channel has not been configured for this command. Ask {} for help!```".format(ctx.message.server.me.display_name))
                    return
                if not ('nsfw' in ctx.message.channel.name or 'fap' in ctx.message.channel.name or 'test-for-sea-cow' in ctx.message.channel.name or 'lood' in ctx.message.channel.name or 'lewd' in ctx.message.channel.name or 'illow ' in str(ctx.message.server.name) or 'hentai' in str(ctx.message.server.name) or 'lewd' in str(ctx.message.server.name) or 'lood' in str(ctx.message.server.name)):
                    await self.bot.say('`This isn\'t a lood channel silly`')
                    return
        elif ctx.message.channel.is_private:
            pass
        headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
        }
        global base_url
        global lood_pics
        content = content.replace(':', '%3A')
        xml = False
        pre = "-"
        extra = ""
        if site == pre+'idol' or site == pre+'chan':
            site = site[1:]
            base_url = 'https://{}.sankakucomplex.com/post/show/'.format(site)
            site1 = 'https://{}.sankakucomplex.com/post/index.json?'.format(site)
            extra = "login=PrivateSeaCow&password_hash=b7fbb42ec61579384e5be04657ee6c3347b407b1&"
            headers = {
                'User-agent': 'SCChannelApp/2.3 (Android; black)'
            }
            xml = True
        elif site == pre+'danbooru':
            site = site[1:]
            base_url = 'https://danbooru.donmai.us/posts/'
            site1 = "https://danbooru.donmai.us/posts.json?"
            extra = "login=PrivateSeaCow&api_key=sJxLSwAQmMXDeleBmStVj0BxEoqdy7308bbfyLjyZ9c&"
        elif site == pre+'konachan':
            site = site[1:]
            base_url = 'https://konachan.com/post/show/'
            site1 = 'https://konachan.com/post/index.json?'
        elif site == pre+'3dbooru':
            site = site[1:]
            base_url = 'http://behoimi.org/post/show/'
            site1 = 'http://behoimi.org/post/index.json?'
            extra = "login=PrivateSeaCow&password_hash=e65d4893e1c5340ce4c61efc01e8595a9f301f4e&"
        elif site == pre+'yande.re' or site == pre+'yandere':
            site = site[1:]
            base_url = 'https://yande.re/post/show/'
            site1 = 'https://yande.re/post.json?'
        elif site == pre+'ibsearch':
            site = site[1:]
            base_url = 'https://ibsearch.xxx/images/'
            site1 = 'https://62A2405DE17E5D287C41C445A076DD4E08E85961@ibsearch.xxx/api/v1/images.json?'
        else:
            content = site+" "+content
            site = "danbooru"
            base_url = 'https://danbooru.donmai.us/posts/'
            site1 = "https://danbooru.donmai.us/posts.json?"
            extra = "login=PrivateSeaCow&api_key=sJxLSwAQmMXDeleBmStVj0BxEoqdy7308bbfyLjyZ9c&"

        if site == 'ibsearch':
            url = site1+extra+'limit=20&q=rating%3Ae+random%3A+-site:furrybo,e621,Überbooru,Xbooru,rule34+'+urlify(content, '+')
            safe_url = base_url+'limit=20&q=rating%3Ae+random%3A+-site:furrybo,e621,Überbooru,Xbooru,rule34+'+urlify(content, '+')
        elif site == 'danbooru':
            url = site1+extra+'limit=20&random=true&tags=rating%3Ae+-bestiality+'+urlify(content, '+')
            safe_url = site1+'limit=20&tags=rating%3Ae+order%3Arandom+'+urlify(content, '+')
        elif site == '3dbooru':
            url = site1+extra+'limit=20&tags=rating%3Ae+order%3Arandom+'+urlify(content, '+')
            safe_url = site1+'limit=20&tags=rating%3Ae+order%3Arandom+'+urlify(content, '+')
        elif site == 'yandere' or site == 'yande.re':
            url = site1+extra+'limit=20&tags=rating%3Ae+order%3Arandom+-partial_scan+'+urlify(content, '+')
            safe_url = site1+'limit=20&tags=rating%3Ae+order%3Arandom+-partial_scan+'+urlify(content, '+')
        else:
            url = site1+extra+'limit=20&tags=rating%3Ae+order%3Arandom+'+urlify(content, '+')
            safe_url = site1+'limit=20&tags=rating%3Ae+order%3Arandom+'+urlify(content, '+')
        r = requests.get(url, headers=headers)
        #r = request.urlopen(url).read()
        safe_url = safe_url.replace(".json", "")
        if r.status_code == 200:
            if not xml:
                if r.text == '[]':
                    embed = discord.Embed(title="Search Turned up no results", url=safe_url, description="Try using a different source | Example: {}{} -konachan {}".format(ctx.prefix, ctx.invoked_with, content))
                    #await self.bot.say('`Search turned up no results, try a different source.`\n'+url.replace('.json',''))
                    await self.bot.say(embed=embed)
                else:
                    search = r.json()[0]
                    url_thing = base_url+str(search['id'])
                    embed = discord.Embed(title="NSFW Image", url=url_thing, description="""[Search Results](%s)""" % (safe_url.replace('.json','')))

                    if site == 'chan' or site == 'idol':
                        #for url in r.json():
                            ftype = str(search['file_url']).replace('?'+str(search['id']), '')
                            ftype = ftype[-3:]
                            file_url = 'https:'+search['file_url']
                            await download_file(file_url, "searches/"+site+'/'+content+'/', search['id'], ftype)
                    elif site == 'ibsearch':
                        #for url in r.json():
                            ftype = str(search['format'])
                            file_url = str('https://'+search['server']+'.ibsearch.xxx/'+search['path'])
                            await download_file(file_url, "searches/"+site+'/'+content+'/', str(search['id']), ftype)
                    elif site == 'danbooru':
                        #stuff = ['https://danbooru.donmai.us/posts/'+url['site_id']+'.json' for url in r.json()]
                        #for url in r.json():
                        #file_url = str('https://'+search['server']+'.ibsearch.xxx/'+search['path'])
                        file_url = str("https://danbooru.donmai.us/"+search["file_url"])
                        await download_file(file_url, "searches/"+site+'/'+content+'/', str(search['id']), str(search['file_ext']))
                    else:
                        #for url in r.json():
                            ftype = str(search['file_url']).split('.')[-1]
                            file_url = search['file_url']
                            if not file_url.startswith("http:"):
                                file_url = "http:"+file_url
                            await download_file(file_url, "searches/"+site+'/'+content+'/', str(search['id']), ftype)
                            
                    if file_url.startswith("http"):
                        embed.set_image(url=file_url)
                    else:
                        print(file_url)
                        pass
                    embed.set_footer(text="Image might take awhile to appear | Disclaimer: The Cow is not resposible for what has been searched")
                    await self.bot.say(embed=embed)
            elif xml:
                #TODO: Allow XML
                pass
        elif r.status_code == 503:
            await self.bot.say("`Error: Service Unavailable. Please Try again later!~`")
        else:
            await self.bot.say('Error: `Status Code: '+str(r.status_code)+'`')

    async def search_pictures(message):
        msg = ctx.message.content.split(' ')
        content = ' '.join(msg[1:])
        headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
        }
        base_url = 'https://ibsear.ch/images/'
        site = 'https://ibsear.ch/api/v1/images.json?'
        stuff = '&limit=5&q=random%3A '
        url = site+stuff+content
        r = requests.get(str(url))
        await bot.say("\n".join(['https://ibsear.ch/images/'+result['id'] for result in r.json()]))

    @commands.command(name="getlewds", pass_context=True, aliases=['getimages','gi'])
    @checks.is_owner()
    async def get_lewds_from_channel(self, ctx, amount = "100", days=5, *, member : discord.Member = None):
        await self.bot.delete_message(ctx.message)
        channel = ctx.message.channel
        today = datetime.datetime.utcnow()
        date = today - datetime.timedelta(days=days)
        await self.get_lewds_extra(ctx, [channel], amount, days)
        pass

    @commands.command(name="getserverlewds", pass_context=True, aliases=['getserverimages','gsi'])
    @checks.is_owner()
    async def get_lewds_from_channel(self, ctx, amount = "100", days=5, serverid = None):
        if serverid == None:
            server = ctx.message.server
        else:
            try:
                server = self.bot.get_server(serverid)
            except:
                return
        await self.bot.delete_message(ctx.message)
        #channel = ctx.message.channel
        await self.get_lewds_extra(ctx, server.channels, amount, days)

    async def get_lewds_extra(self, ctx, channels, amount, days):
        today = datetime.datetime.utcnow()
        date = today - datetime.timedelta(days=days)
        for channel in channels:
            async for msg in self.bot.logs_from(channel, limit=int(amount), after=date):
                if msg.attachments:
                    for pic in msg.attachments:
                        if len(msg.attachments) >=2:
                            rand = str(msg.id)+"_"+str(random.randint(1, 100))
                        else:
                            rand = msg.id
                        file_name = str(rand)
                        try:
                            await download_file(str(pic['url']), "{}/{}".format(channel.server.name.replace("/","-"), channel.name), str(file_name), str(pic['url'].split('.')[-1]), False)
                        except:
                            pass
                elif msg.embeds:
                    for pic in msg.embeds:
                        if len(msg.embeds) >=2:
                            rand = str(msg.id)+"_"+str(random.randint(1, 100))
                        else:
                            rand = msg.id
                        file_name = str(rand)
                        if "url" not in pic:
                            return
                        try:
                            file_format = pic['format']
                        except:
                            file_format = pic['url'].split('.')[-1][:3]
                        try:
                            await download_file(str(pic['url']), "{}/{}".format(channel.server.name.replace("/","-"), channel.name), str(file_name), str(file_format), False)
                        except:
                            pass

    @commands.group(name="nsfwconfig", pass_context=True)
    @checks.is_owner()
    async def lewd_config(self, ctx):
        pass

    @lewd_config.command(name="addchannel", pass_context=True, aliases=["add"])
    async def add_channel_nsfwconfig(self, ctx, *, channel : discord.Server = None):
        await self.bot.delete_message(ctx.message)
        if channel == None:
            channel = ctx.message.channel
        server = ctx.message.channel.server
        serverfp = "./data/config/servers/{}".format(server.id)
        if not os.path.isfile(serverfp+"/nsfw_settings.ini"):
            path = serverfp+"/nsfw_settings.ini"
            await make_nsfw_config(path)

        nsfw_config = configparser.ConfigParser()
        path = "./data/config/servers/{}/nsfw_settings.ini".format(server.id)
        nsfw_config.read(path)
        try:
            nsfw_config["channels"][ctx.message.channel.id] = "true"
        except:
            nsfw_config["channels"] = {ctx.message.channel.id: "true",}

        with open(path, 'w') as configfile:
            nsfw_config.write(configfile)
        pass

    async def on_message(self, message):
        if message.type !=  discord.MessageType.default:
            return
        msgcontent = message.content.lower()
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content)
        imgurlink = re.findall("(https?)\:\/\/(?:i\.)?(www\.)?(?:m\.)?imgur\.com\/(gallery\/|a\/|r\/[a-z]+)?(?:\/)?([a-zA-Z0-9]+)(#[0-9]+)?(?:\.gifv)?", message.content)
        imgurmatch = re.match("(https?)\:\/\/(?:i\.)?(www\.)?(?:m\.)?imgur\.com\/(gallery\/|a\/|r\/[a-z]+)?(?:\/)?([a-zA-Z0-9]+)(#[0-9]+)?(?:\.gifv)?", message.content)
        r_image = re.compile(r".*\.(jpg|png|gif|webm|jpeg)$")
        chantype = message.channel.type
        if chantype ==  discord.ChannelType.private:
            is_private = True
            channame = "@pms/"+message.author.discriminator
        elif chantype == discord.ChannelType.group:
            is_private = True
            channame = "@groups/"+message.channel.name
        elif chantype == discord.ChannelType.voice:
            return
        else:
            is_private = False
            servername = message.server.name.replace("/","-")
            channelname = message.channel.name.replace("/","-")
            channame = "{0}/{1}".format(servername, channelname)
        try:
            if (not is_private) and imgurmatch and self.use_imgur:
                try:
                    for lnk in imgurlink:
                        if ('nsfw' in message.channel.name.lower() or 'fap' in message.channel.name.lower() or 'lood' in message.channel.name.lower() or 'lewd' in message.channel.name.lower() or 'pillow' in str(message.server.name).lower() or 'hentai' in str(message.server.name).lower() or 'lewd' in str(message.server.name).lower() or 'lood' in str(message.server.name).lower()):
                            name = str(message.server.name)+'/'+str(message.channel.name)+'/@imgur/'
                        else:
                            name = str(message.server.name)+'/'+str(message.channel.name)+'/'+str(message.author.name)+'/@imgur/'
                            break
                        for pic in self.imgur.get_album_images(lnk[3]):
                            if pic.animated:
                                thing = str(pic.link).split('/')
                                imagething = str(self.imgur.get_album(lnk[3]).id)
                                await download_file(str(pic.webm), name+imagething, str(thing[-1].split('.')[-2]), 'webm', False)
                            else:
                                thing = str(pic.link).split('/')
                                await download_file(str(pic.link), name+imagething, str(thing[-1].split('.')[-2]), str(thing[-1].split('.')[-1]), False)
                except:
                    for lnk in imgurlink:
                        if ('nsfw' in message.channel.name or 'fap' in message.channel.name or 'lood' in message.channel.name or 'lewd' in message.channel.name or 'illow ' in str(message.server.name) or 'hentai' in str(message.server.name) or 'lewd' in str(message.server.name) or 'lood' in str(message.server.name)):
                            name = str(message.server.name)+'/'+str(message.channel.name)+'/@imgur'
                        else:
                            name = str(message.server.name)+'/'+str(message.channel.name)+'/'+str(message.author.name)+'/@imgur'
                            break
                        pic = self.imgur.get_image(lnk[3])
                        if pic.animated:
                            thing = str(pic.link).split('/')
                            await download_file(str(pic.webm), name, str(thing[-1].split('.')[-2]), 'webm', False)
                        else:
                            thing = str(pic.link).split('/')
                            await download_file(str(pic.link), name, str(thing[-1].split('.')[-2]), str(thing[-1].split('.')[-1]), False)
            elif ((message.embeds) or (message.attachments)) and (not imgurmatch):
                if not is_private:
                    if message.server.name == "BetterDiscord" or message.server.name == "pixeltailgames" or message.server.name == 'Discord API' or message.server.id == "207789872264642570":
                        return
                    if 'nsfw' in message.channel.name.lower() or 'fap' in message.channel.name.lower() or 'lood' in message.channel.name.lower() or 'lewd' in message.channel.name.lower() or "hentai" in str(message.server.name.lower()) or 'pillow ' in str(message.server.name.lower()) or 'hentai' in str(message.server.name).lower() or 'lewd' in str(message.server.name).lower() or 'lood' in str(message.server.name).lower():
                        name = channame
                    else:
                        return
                        name = channame+"/"+message.author.name
                    if message.author.id == "134786874920140800":
                        name+="/Aba's Dumps"
                    if message.server.id != "107883969424396288" and message.author == message.server.me:
                        return
                elif is_private:
                    name = channame
                if message.embeds:
                    for pic in message.embeds:
                        if pic["type"] == "image":
                            url = pic["url"]
                        elif pic["type"] == "rich" and "image" in pic:
                            url = pic["image"]["url"]
                        else:
                            return
                        filename = url.split("/")[-1]
                        filename1 = filename.split('.')
                        filename2 = filename1[1]
                        filename1 = message.id
                        try:
                            await download_file(str(url), name, filename1, filename2, False)
                        except:
                            pass
                elif message.attachments:
                    for pic in message.attachments:
                        url = pic['url']
                        filename = pic['filename']
                        filename1 = filename.split('.')
                        filename2 = filename1[1]
                        filename1 = message.id
                        try:
                            await download_file(str(url), name, filename1, filename2, False)
                        except:
                            pass
                elif r_image.match(urls[0]):
                    for pic in urls:
                        thing = str(pic).split('/')
                        try:
                            await download_file(str(pic), name, str(thing[-1].split('.')[-2]), str(thing[-1].split('.')[-1]), False)
                        except:
                            pass
                else:
                    print('ERROR!! |'+str(pic['url'])+'|auto downloads/'+name+'|'+str(thing[-1].split('.')[-2])+'|'+str(thing[-1].split('.')[-1]))
        except Exception as e:
            if type(e) != discord.errors.NotFound and message.author == message.server.me:
                raise
            return

def setup(bot):
    n = nsfw(bot)
    bot.add_cog(n)