import asyncio
import discord
from discord.ext import commands
from time import sleep
import cogs.utils.checks as checks

class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '```xl\n{0.title} uploaded by {0.uploader} and requested by {1.display_name}```'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, 'B-BAKA!!! Your song is on: ```' + str(self.current)+"```")
            self.current.player.start()
            await self.play_next_song.wait()

class music:
    """Music Commands"""
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions()
    async def join(self, ctx, *, channel : discord.Channel):
        """Joins a voice channel."""
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await self.bot.say('B-but I can only be in one voice channel. B-BAKA!! >:T')
        except discord.InvalidArgument:
            await self.bot.say('*starts to panic* :persevere: :sweat_drops: T-That\'s not a voice channel.')
        else:
            await self.bot.say('I-It\'s not like I wanna play music in `' + channel.name + '`. B-BAKA!!')

    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say('*starts to panic* Y-You\'re not in a v-voice channel >.<;')
            return False
        if 'usic' not in summoned_channel.name and not checks.mod_or_permissions():
            await self.bot.say('That\'s not a music channel. And I don\'t wanna join because you\'re there!!')
            return False
        elif checks.mod_or_permissions():
            pass
        else:
            return

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song : str):
        """Plays a song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'It\'s not like I got the error for you. B-BAKA!!: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
            raise
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await self.bot.say('It\'s not like I added this for you: ' + str(entry))
            await state.songs.put(entry)

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx, value : int):
        """Sets the volume of the currently playing song."""

        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            await self.bot.say('It\'s not like I wanted to set the volume for you: {:.0%}'.format(player.volume))

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        """Pauses the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()
            await self.bot.say(':pause_button:')

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """Resumes the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions()
    async def stop(self, ctx):
        """Stops playing audio and leaves the voice channel.
        This also clears the queue.
        """
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
        except:
            raise

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        """Vote to skip a song. The song requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('*whispers* But there\'s no music playing. >:T')
            return

        voter = ctx.message.author
        if voter.id == "105800900521570304":
        #if checks.mod_or_permissions(): #Todo: Make it so the mods and admins can force skip
            await self.bot.say('I\'m skipping this song because master said to.')
            state.skip()
        elif voter == state.current.requester:
            await self.bot.say('It\'s not like I skipped that song for you, {0}! B-BAKA!!!'.format(ctx.message.author.display_name))
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                await self.bot.say('It\'s not like I wanted people to skip. B-BAKA!!')
                state.skip()
            else:
                await self.bot.say('[{}/3] votes and I\'ll skip this song. HUMPF! >:T'.format(total_votes))
        else:
            await self.bot.say('You already voted!! B-BAKA!!!')

    @commands.command(pass_context=True, no_pm=True)
    async def playing(self, ctx):
        """Shows info about the currently played song."""

        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            await self.bot.say('*whispers* B-but there\'s no music playing. >:T')
        else:
            skip_count = len(state.skip_votes)
        await self.bot.say('Im playing {}. Of course not for you! B-BAKA!!! [skips: {}/3]'.format(state.current, skip_count))

    @commands.command(pass_context=True, no_pm=True, name='list', hidden=True)
    @checks.is_owner()
    async def _list(self, ctx):
        """Shows a list of the currently queued songs."""
        server = ctx.message.server
        state = self.get_voice_state(server)

        songs = '\n'.join(list(state.songs.get))
        currently_playing = "__**Currently playing:**__ `{}`\n".format(state.current)
        msg = currently_playing + '===========================\n' + songs
        pass



def setup(bot):
    n = music(bot)
    bot.add_cog(n)
