import json
import requests
import re
import os
import discord
import time
import datetime
from discord.ext import commands, tasks

# TOKEN has been changed after code made public into github
with open('token.txt') as f:
    TOKEN = f.readline()
    f.close()
file_location = "youtubedata.json"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix = "!", intents = intents, help_command=None)

@bot.event
async def on_ready():
    print("Bot Now Online!")
    checkforvideos.start()

@tasks.loop(seconds=2)
async def checkforvideos():
    
    try:
        f = open(file_location, "r", encoding='utf-8')
        data = json.load(f)
        f.close()
    except FileNotFoundError:
        print(f"請至{file_location}更新使用者資訊\n Please update your info at {file_location}")
        with open(file_location, 'w', encoding='utf-8') as f:
            writeData = {"(Youtube帳號代碼 - Youtube Handle)": {"channel_name": "(想寫什麼都可以 - write what ever you want)", "who_to_mention": "(everyone / none / roleID)", "latest_video_url": "(會自行偵測，不必填寫 - it'll detect itself, you can leave it blank)", "latest_shorts_url": "(會自行偵測，不必填寫 - it'll detect itself, you can leave it blank)", "notifying_discord_channel": "(discord頻道ID - discord Channel ID)"}}
            f.write(str(writeData))
            f.close()
            time.sleep(10)
            return 0
    
    for youtube_channel in data:
        channel = f"https://www.youtube.com/@{youtube_channel}"
        channel_name = data[youtube_channel]["channel_name"]
        who_to_mention = data[youtube_channel]["who_to_mention"]
        
        match who_to_mention:
            case "everyone":
                who_to_mention = "@everyone"
            case "none":
                who_to_mention = ""
            case _:
                who_to_mention = "<@&" + who_to_mention + ">"
        
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

            with open(file_location, "w", encoding='utf-8') as f:
                json.dump(data, f)
                f.close()

            discord_channel_id = data[str(youtube_channel)]["notifying_discord_channel"]
            discord_channel = bot.get_channel(int(discord_channel_id))

            msg = f"{who_to_mention} {channel_name}發布了新影片!\n{latest_video_url}"

            await discord_channel.send(msg)
            print(f'[{datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")} INFO] New Video Info Sent!')
    
        # New Shorts Mentioning
        if not str(data[youtube_channel]["latest_shorts_url"]) == latest_shorts_url:

            data[str(youtube_channel)]["latest_shorts_url"] = latest_shorts_url

            with open(file_location, "w", encoding='utf-8') as f:
                json.dump(data, f)
                f.close()

            discord_channel_id = data[str(youtube_channel)]["notifying_discord_channel"]
            discord_channel = bot.get_channel(int(discord_channel_id))

            msg = f"{who_to_mention} {channel_name}發布了新的shorts!\n{latest_shorts_url}"

            await discord_channel.send(msg)
            print(f'[{datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")} INFO] New Shorts Info Sent!')
    
    # temporary disable to cooldown and test for a while to see if multiple mentions will be re-sent incorrectly
    # time.sleep(300)

bot.run(TOKEN)
