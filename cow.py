import discord
from discord.ext import commands
from ctypes.util import find_library

description = """
♡ Moe Cow's Music bot ♡
FRED IS A HORRIBLE CODER >:T
"""

bot = commands.Bot(command_prefix=["~~", '='], description=description, pm_help=False)

if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus('libopus.1a')

@bot.event
async def on_ready():
    bot.load_extension('cogs.general')
    bot.load_extension('cogs.moderation')
    bot.load_extension('cogs.music')
    print('------')
    print('Currently logged in as ['+bot.user.name+' (ID: "'+bot.user.id+'")]')
    print('Number of Servers Connected: '+str(len(list(bot.servers))))
    print('Current Prefix: '+', '.join(bot.command_prefix))
    print('------')

@bot.event
async def on_message(message):
    try:
        await process_commands(message)
    except Exception as e:
        await bot.say('It\'s not like I got the error for you. B-BAKA!!: ```py\n{}: {}\n```'.format(type(e).__name__, e))
        raise

f = open('credentials.txt', 'r')
BOT_TOKEN = f.read()
f.close()


bot.run(BOT_TOKEN)
