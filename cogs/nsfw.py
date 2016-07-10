import asyncio
import discord
from discord.ext import commands
import re
import requests
import os
from time import sleep
import cogs.utils.checks as checks

def urlify(s, k):

    # Remove all non-word characters (everything except numbers and letters)
    #s = re.sub(r"[^\w\s]", '', s)

    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", k, s)

    return s

class nsfw:
    """Commands that are nsfw."""
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(pass_context=True, help='Send nsfw images using \'content\' as tags.\nSites you can currently use: konachan, chan, ibsearch, yandere.\nSites currently being added: Danbooru, idol.', brief='''Send nsfw images using 'content' as tags.''')
    async def lood(self, ctx, site : str, *, content : str):
        if "gore" in content or 'furry' in content:
            return
        await self.bot.type()
        global base_url
        if not ('nsfw' in ctx.message.channel.name or 'fap' in ctx.message.channel.name or 'test-for-sea-cow' in ctx.message.channel.name or 'lood' in ctx.message.channel.name or 'lewd' in ctx.message.channel.name or 'illow ' in str(ctx.message.server.name) or 'hentai' in str(ctx.message.server.name) or 'lewd' in str(ctx.message.server.name) or 'lood' in str(ctx.message.server.name)):
            await self.bot.say('`This isn\'t a lood channel silly`')
            return
        try:
            site = site
        except:
            await self.bot.say( '''`USAGE: {0}lood <chan|konachan|ibsearch> <tags> (NOTE: 'chan' isn't random)`'''.format(p))
            return
        if site == "danbooru" and (ctx.message.channel.name != 'test-for-sea-cow'):
            await self.bot.say('''Unfortunately 'Danbooru' doesn't work (I am fixing this don't worry)''')
            return
        headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
        }
        content = content.replace(':', '%3A')
        if site == 'chan':
            base_url = 'https://chan.sankakucomplex.com/post/show/'
            site1 = 'https://chan.sankakucomplex.com/post/index.json?login=privateseacow&password_hash=b7fbb42ec61579384e5be04657ee6c3347b407b1'
        elif site == 'idol':
            base_url = 'https://idol.sankakucomplex.com/post/show/'
            site1 = 'https://idol.sankakucomplex.com/post/index.json?login=privateseacow&password_hash=b7fbb42ec61579384e5be04657ee6c3347b407b1'
        elif site == 'danbooru':
            base_url = 'https://danbooru.donmai.us/posts/'
            site1 = 'https://ibsearch.xxx/api/v1/images.json?'
        elif site == 'konachan':
            base_url = 'https://konachan.com/post/show/'
            site1 = 'https://konachan.com/post/index.json?'
        elif site == '3dbooru':
            base_url = 'http://behoimi.org/post/show/'
            site1 = 'http://behoimi.org/post/index.json?'
        elif site == 'yande.re' or site == 'yandere':
            base_url = 'https://yande.re/post/show/'
            site1 = 'https://yande.re/post.json?'
        elif site == 'ibsearch':
            base_url = 'https://ibsearch.xxx/images/'
            site1 = 'https://ibsearch.xxx/api/v1/images.json?'
        else:
            await self.bot.say('**Error:** `UNKNOWN SOURCE`')
            return
        if site == 'ibsearch':
            url = site1+'key=62A2405DE17E5D287C41C445A076DD4E08E85961&limit=5&q=rating%3Ae+random%3A+-site:furrybo,safebooru,e621,Überbooru,Xbooru,rule34+'+urlify(content, '+')
        elif site == 'danbooru':
            url = site1+'key=62A2405DE17E5D287C41C445A076DD4E08E85961&limit=5&sources=one&q=rating%3Ae+random%3A+site:danbooru+'+urlify(content, '+')
        elif site == '3dbooru':
            url = site1+'login=PrivateSeaCow&password_hash=e65d4893e1c5340ce4c61efc01e8595a9f301f4e&limit=5&tags=rating%3Ae+order%3Arandom+'+urlify(content, '+')
        elif site == 'yandere':
            url = site1+'limit=5&tags=rating%3Ae+order%3Arandom+-partial_scan+'+urlify(content, '+')
        else:
            url = site1+'limit=5&tags=rating%3Ae+order%3Arandom+'+urlify(content, '+')
        r = requests.get(url, headers=headers)
        #r = request.urlopen(url).read()
        if r.status_code == 200:
            if r.text == '[]':
                await self.bot.say('`Search turned up no results, try a different source.`\n'+url.replace('.json',''))
            else:
                global lood_pics
                lood_pics = []
                if site == 'danbooru':
                    lood_pics = [str(result['site_id']) for result in r.json()]
                else:
                    lood_pics = [str(result['id']) for result in r.json()]

                if site == 'chan' or site == 'idol':
                    await self.bot.say("\n".join(['https:'+result['file_url'] for result in r.json()]))
                    #for url in r.json():
                        #ftype = str(url['file_url']).replace('?'+str(url['id']), '')
                        #ftype = ftype[-3:]
                        #await download_file('https:'+url['file_url'], "searches\\"+site+'\\'+content+'\\', url['id'], ftype)
                elif site == 'ibsearch':
                    #await self.bot.say("\n".join([str('https://'+result['server']+'.ibsearch.xxx/'+result['path']) for result in r.json()]))
                    await self.bot.say("\n".join([str('https://ibsearch.xxx/images/'+result['id']+'#image') for result in r.json()]))
                    #for url in r.json():
                        #ftype = str(url['format'])
                        #await download_file(str('https://'+url['server']+'.ibsearch.xxx/'+url['path']), "searches\\"+site+'\\'+content+'\\', str(url['id']), ftype)
                elif site == 'danbooru':
                    stuff = ['https://danbooru.donmai.us/posts/'+url['site_id']+'.json' for url in r.json()]
                    for url2 in stuff:
                        s = requests.get(url2, headers=headers)
                        try:
                            print(s.json()['file_url'])
                            stuff2 = ['https://danbooru.donmai.us'+s.json()['file_url']]
                        except:
                            print(s.json()['https://danbooru.donmai.us/posts/'+url['site_id']])
                    await self.bot.say('https://danbooru.donmai.us'+"\n'https://danbooru.donmai.us'".join(stuff2))
                    #for url in r.json():
                        #await download_file(str('https://'+url['server']+'.ibsearch.xxx/'+url['path']), "searches\\"+site+'\\'+content+'\\', str(url['id']), str(url['format']))
                else:
                    await self.bot.say("\n".join([result['file_url'] for result in r.json()]))
                    #for url in r.json():
                        #ftype = str(url['file_url']).split('.')[-1]
                        #await download_file(url['file_url'], "searches\\"+site+'\\'+content+'\\', str(url['id']), ftype)
        elif r.status_code == 500 and site == 'danbooru':
            await self.bot.say('ERROR: Danbooru doesn\'t like tags.')
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

    @commands.command(name='getlood', aliases=['gl'], pass_context=True, hidden=True)
    async def get_lood_pic(self, ctx, number=None):
        '''Get the recent pics from a lood search.'''
        if lood_pics == None:
            await self.bot.say(":cherry_blossom: Search something first! :cherry_blossom:")
            return
        if base_url == None:
            await self.bot.say(":cherry_blossom: Search something first! :cherry_blossom:")
            return
        try:
            if number == None:
                await self.bot.say(base_url+str(lood_pics[int(number)-1]))
                sleep(3)
                await self.bot.delete_message(ctx.message)
            else:
                await self.bot.say(str(base_url+('\n'+base_url).join(lood_pics)))
                sleep(3)
                await self.bot.delete_message(ctx.message)
        except:
            await self.bot.say(":cherry_blossom: Search something first! :cherry_blossom:")
            raise

def setup(bot):
    n = nsfw(bot)
    bot.add_cog(n)
