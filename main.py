# https://discordapp.com/api/oauth2/authorize?client_id=1248612928601722971&permissions=8&scope=bot

import json
import requests
import re
import os
import discord
import time
import datetime
from discord.ext import commands, tasks

TOKEN = "MTI0ODYxMjkyODYwMTcyMjk3MQ.G5S47Z.R7AgWZxHpvW_eECbxbJ-tSTpChBJZffSaM_KMY"
file_location = "youtubedata.json"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix = "!", intents = intents, help_command=None)

@bot.event
async def on_ready():
    print("Bot Now Online!")
    checkforvideos.start()

@tasks.loop(seconds=2)
async def checkforvideos():
    with open(file_location, "r") as f:
        data = json.load(f)
    for youtube_channel in data:
        channel = f"https://www.youtube.com/channel/{youtube_channel}"
    
        videos = requests.get(channel+"/videos").text
        shorts = requests.get(channel+"/shorts").text
    
        try:
            latest_video_url = "https://www.youtube.com/watch?v=" + re.search('(?<="videoId":").*?(?=")', videos).group()
            latest_shorts_url = "https://www.youtube.com/shorts/" + re.search('(?<="videoId":").*?(?=")', shorts).group()
        except:
            continue
    
        # New Video Mentioning
        if not str(data[youtube_channel]["latest_video_url"]) == latest_video_url:

            data[str(youtube_channel)]["latest_video_url"] = latest_video_url

            with open(file_location, "w") as f:
                json.dump(data, f)

            discord_channel_id = data[str(youtube_channel)]["notifying_discord_channel"]
            discord_channel = bot.get_channel(int(discord_channel_id))

            msg = f"@everyone\n{latest_video_url}"

            await discord_channel.send(msg)
            print(f'[{datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")} INFO] New Video Info Sent!')
    
        # New Shorts Mentioning
        if not str(data[youtube_channel]["latest_shorts_url"]) == latest_shorts_url:

            data[str(youtube_channel)]["latest_shorts_url"] = latest_shorts_url

            with open(file_location, "w") as f:
                json.dump(data, f)

            discord_channel_id = data[str(youtube_channel)]["notifying_discord_channel"]
            discord_channel = bot.get_channel(int(discord_channel_id))

            msg = f"@everyone\n{latest_shorts_url}"

            await discord_channel.send(msg)
            print(f'[{datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")} INFO] New Shorts Info Sent!')
    
    time.sleep(300)

bot.run(TOKEN, log_handler=None)
