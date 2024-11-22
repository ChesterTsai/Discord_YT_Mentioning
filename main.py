# All the comments written in this file haven't been re-write.
# Just look at the codes, not the comments
# I don't wanna give any fucks about the comments

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

    #starting checking for vidoes everytime the bot's go online
    checkforvideos.start()

#checking for vidoes every 30 seconds
#you can check for vidoes every 10 seconds also but i would prefer to keep 30 seconds
@tasks.loop(seconds=30)
async def checkforvideos():
  with open(file_location, "r") as f:
    data=json.load(f)

  #printing here to show
  #print("Now Checking!")

  #checking for all the channels in youtubedata.json file
  for youtube_channel in data:
    #print(f"Now Checking For {data[youtube_channel]['channel_name']}")
    #getting youtube channel's url
    channel = f"https://www.youtube.com/channel/{youtube_channel}"

    #getting html of the /videos page
    html = requests.get(channel+"/videos").text

    #getting the latest video's url
    #put this line in try and except block cause it can give error some time if no video is uploaded on the channel
    try:
      latest_video_url = "https://www.youtube.com/watch?v=" + re.search('(?<="videoId":").*?(?=")', html).group()
    except:
      continue

    #checking if url in youtubedata.json file is not equals to latest_video_url
    if not str(data[youtube_channel]["latest_video_url"]) == latest_video_url:

      #changing the latest_video_url
      data[str(youtube_channel)]['latest_video_url'] = latest_video_url

      #dumping the data
      with open(file_location, "w") as f:
        json.dump(data, f)

      #getting the channel to send the message
      discord_channel_id = data[str(youtube_channel)]['notifying_discord_channel']
      discord_channel = bot.get_channel(int(discord_channel_id))

      #sending the msg in discord channel
      #you can mention any role like this if you want
      msg = f"@everyone\n{latest_video_url}"
      #if you'll send the url discord will automaitacly create embed for it
      #if you don't want to send embed for it then do <{latest_video_url}>

      await discord_channel.send(msg)
      print(f'[{datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")} INFO] New Video Info Sent!')
      time.sleep(300)

bot.run(TOKEN, log_handler=None)
