from discord.ext import commands
import discord.utils
import configparser
import bitly_api

config = configparser.ConfigParser()
config.read('./data/config/config.ini')

bitly = bitly_api.Connection(access_token=config.get('bitly','token'))

def waa_shorten(self, url):
    api_key = config["waa"]["key"]
    site = requests.get("https://api.waa.ai/shorten?key={}&url={}".format(api_key, url))
    site = site.json()
    if site["success"] == True and site["status"] == 200:
        return site["data"]
    else:
        return bitly.shorten(url)