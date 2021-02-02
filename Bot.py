import discord
import asyncio
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
import youtube_dl
from random import choice
import ps5_invcheck_target
import wikipediaapi
import lyricsgenius as genius

api = genius.Genius('G-HQPGGHClZk7HTxUF-9rJn98Ll_8jPh78UAkDtAAxkOSHqNx-TX301KVBm9x2F_')

client = commands.Bot(command_prefix = '.')

status = ['Music!', 'Games!', 'Football!']

@client.event
async def on_ready():
    change_status.start()
    print('Utility Bot online.')
    check_target.start()

# Join message for members 
@client.event
async def on_member_join(member):
    print(f'{member} has joined the server.')

# Remove message for members
@client.event
async def on_member_remove(member):
    print(f'{member} has left the sever.')


#help_str = "```Commands:\n.help - Display list of commands\n.play - Play media from youtube\n.wiki - Get information from wikipedia\n.lyric - Get lyrics for songs\n.stock - Get item stock information```"

#@client.command()
#async def help(ctx):
#    await ctx.send(help_str)
    
###################
####### WIKI ######
###################

@client.command(name = 'wiki', help = 'Retreive a page from wikipedia.')
async def wiki(ctx, url):

    wiki_wiki = wikipediaapi.Wikipedia('en')

    page_py = wiki_wiki.page(url)
    
    #S = requests.Session()
    #URL = "https://en.wikipedia.org/w/api.php"
    #PARAMS = {
    #    "action": "opensearch",
    #    "namespace": "0",
    #    "search": url,
    #    "limit": "5",
    #    "format": "json"
    #}
    #R = S.get(url=URL, params=PARAMS)
    #DATA = R.json()
    #print(DATA)

    #links = page_py.links
    #linklist = "```"
    #for title in sorted(links.keys()):
    #    print("%s: %s" % (title, links[title].fullurl))
    #    if links[title].fullurl != "":
    #        linklist += title + " | " + links[title].fullurl + "\n"

    #linklist += "```"
    #print(linklist)
            
    if page_py.exists():
        await ctx.send(page_py.canonicalurl)
    #    await ctx.send(linklist)
    else:
        await ctx.send("```Could not find wiki page \'" + url + "\'```")

################################
#######   Lyrics Finder   ######
################################

@client.command(name = 'lyrics', help = "finds lyrics for a song using 'artist - song' format")
async def botLyrics(ctx, arg):
     arr = arg.split('-')
     a = arr[0]
     s = arr[1]
     await ctx.send('Searching genius lyrics for: \n {} by {}'.format(s, a))
     song_lyrics = api.search_song(s, a).lyrics
     await ctx.send(song_lyrics)

################################
####### Inventory Checker ######
################################
target_url = 'https://www.target.com/c/playstation-5-video-games/-/N-hj96d?lnk=snav_rd_playstation_5'
@tasks.loop(seconds=30)
async def check_target():
    inStock = ps5_invcheck_target.checkTarget()
    if inStock == 1:
        channel = client.get_channel(12324234183172)
        await channel.send(f'ITEM IS NOW IN STOCK: `{target_url}!`')
    else:
        print('Item not in stock')

########################
####### MUSIC BOT ######
########################

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# have the bot join the voice channel
@client.command(name='join', help='This command makes the bot join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel")
        return
    
    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()

# queue holds songs to be played
queue = []

@client.command(name='queue', help='This command adds a song to the queue')
async def queue_(ctx, url):
    global queue

    queue.append(url)
    await ctx.send(f'`{url}` added to queue!')

# remove song from queue
@client.command(name='remove', help='This command removes an item from the list')
async def remove(ctx, number):
    global queue

    try:
        del(queue[int(number)])
        await ctx.send(f'Your queue is now `{queue}!`')
    
    except:
        await ctx.send('Your queue is either **empty** or the index is **out of range**')

# play a song that is queued        
@client.command(name='play', help='This command plays songs')
async def play(ctx):
    global queue

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(queue[0], loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('**Now playing:** {}'.format(player.title))
    del(queue[0])

# pause a song that is currently playing
@client.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.pause()

# resume a paused song
@client.command(name='resume', help='This command resumes the song!')
async def resume(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.resume()

# view song queue
@client.command(name='view', help='This command shows the queue')
async def view(ctx):
    await ctx.send(f'Your queue is now `{queue}!`')

# bot to leave voice channel
@client.command(name='leave', help='This command stops makes the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

# stops song that is currently playing, does not remove from queue
@client.command(name='stop', help='This command stops the song!')
async def stop(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.stop()

# loops status message for bot
@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))
	
client.run('Nzc1ODcxMzMxODE5OTc4ODQy.X6sofA.4SLZTrgdZlmYY4ZtpcLzjtAyt_c')
