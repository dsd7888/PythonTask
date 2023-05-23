import discord
import openai
import asyncio
import datetime
import youtube_dl
import os

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Set up OpenAI API key
openai.api_key = "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"

# Reminder Functionality
async def remind(msg, time):
    await asyncio.sleep(time)
    await msg.channel.send(f"Reminder: {msg.content}")

# Chat Functionality
async def chat(message):
    prompt = f"User: {message.content}\nBot:"
    response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=50).choices[0].text.strip()
    await message.channel.send(response)

# Music Functionality
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL({'format': 'bestaudio/best', 'noplaylist': 'True'}).extract_info(url, download=False))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else youtube_dl.YoutubeDL({'format': 'bestaudio', 'noplaylist': 'True'}).prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, executable="ffmpeg"), data=data)

@client.event
async def on_message(message):
    # Chat Functionality
    if not message.author.bot:
        await chat(message)

    # Reminder Functionality
    if message.content.startswith("!remind"):
        try:
            time = int(message.content.split()[1])
            msg = await message.channel.send(f"Reminder set for {time} seconds")
            asyncio.ensure_future(remind(msg, time))
        except:
            await message.channel.send("Invalid command syntax. Usage: !remind <time in seconds>")

    # Music Functionality
    #Function is running successfully but doesn't work
    elif message.content.startswith("!play"):
        try:
            url = message.content.split()[1]
            voice_channel = message.author.voice.channel
            vc = await voice_channel.connect()
            source = await YTDLSource.from_url(url, loop=client.loop)
            vc.play(source)
        except:
            await message.channel.send("Invalid command syntax. Usage: !play <youtube url>")
    elif message.content.startswith("!stop"):
        try:
            voice_client = message.guild.voice_client
            await voice_client.disconnect()
        except:
            await message.channel.send("Bot is not connected to a voice channel.")

# Run the bot
TOKEN='MTA5NTM0MjcxMDQ4NDkwMTkxOA.Gsw4MI.-LEv1lxfb_yRWodfQF2HUTchDAJGcg0MVUeHA8'
client.run(TOKEN)
