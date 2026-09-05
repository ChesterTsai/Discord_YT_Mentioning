import json
import requests
import re
import os
import discord
import datetime
from discord.ext import commands, tasks

file_location = "data/youtubedata.json"

class ytMention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ytMention(self, ctx):
        """設定Youtube發片通知"""
        
        if not ctx.message.author.guild_permissions.administrator:
            await ctx.channel.send('你沒有此權限')
            return
        
        #check if the author of the text is the same person.
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        
        await ctx.send("請輸入Youtube頻道網址")
        channel_link = await self.bot.wait_for("message", check = check)
        channel_link = channel_link.content

        if "?" in channel_link:
            channel_link = channel_link.split("?")
            channel_link = channel_link[0]

        if channel_link.endswith("/featured"):
            channel_link = channel_link.split("/featured")
            channel_link = channel_link[0]
        elif channel_link.endswith("/videos"):
            channel_link = channel_link.split("/videos")
            channel_link = channel_link[0]
        elif channel_link.endswith("/shorts"):
            channel_link = channel_link.split("/shorts")
            channel_link = channel_link[0]
        elif channel_link.endswith("/streams"):
            channel_link = channel_link.split("/streams")
            channel_link = channel_link[0]
        elif channel_link.endswith("/playlists"):
            channel_link = channel_link.split("/playlists")
            channel_link = channel_link[0]
        elif channel_link.endswith("/posts"):
            channel_link = channel_link.split("/posts")
            channel_link = channel_link[0]

        await ctx.send("請輸入頻道名稱(新影片發布時機器人稱呼你的方法)")
        channel_name = await self.bot.wait_for("message", check = check)
        channel_name = channel_name.content
        
        who_to_mention_msg = "你想要通知哪些人？"
        who_to_mention_msg += "\n\t輸入「everyone」 -> 通知所有人"
        who_to_mention_msg += "\n\t輸入「none」 -> 純文字通知"
        who_to_mention_msg += "\n\t輸入身分組ID(@該身分組並在最前面加上一個「\\\」後enter) -> 通知該身分組"
        await ctx.send(who_to_mention_msg)
        who_to_mention = await self.bot.wait_for("message", check = check)
        who_to_mention = who_to_mention.content
        if who_to_mention.startswith("\\<@&"):
            who_to_mention = who_to_mention[4:-1]
        
        await ctx.send("是否傳送影片縮圖 (y/n)")
        sendThumbnail = await self.bot.wait_for("message", check = check)
        sendThumbnail = sendThumbnail.content
        if sendThumbnail.lower() != "y" and sendThumbnail.lower() != "n":
            await ctx.channel.send('錯誤的選項')
            return
        
        await ctx.send("請輸入接收通知的discord頻道ID")
        notifying_discord_channel = await self.bot.wait_for("message", check = check)
        notifying_discord_channel = notifying_discord_channel.content
        if not self.bot.get_channel(int(notifying_discord_channel)):
            await ctx.channel.send('錯誤的頻道ID')
            return
        notifying_discord_guild = self.bot.get_channel(int(notifying_discord_channel)).guild.id
        if notifying_discord_guild != ctx.guild.id:
            await ctx.channel.send('基於安全性原因，請勿對其他伺服器的頻道進行操作')
            return
        writeData(channel_link, channel_name, who_to_mention, sendThumbnail.lower(), notifying_discord_channel)
        await ctx.send("寫入成功!")

async def setup(bot):
    await bot.add_cog(ytMention(bot))

def readData():
    
    try:
        with open(file_location, "r", encoding='utf-8') as f:
            data = json.load(f)
            f.close()
    except FileNotFoundError:
        with open(file_location, 'w', encoding='utf-8') as f:
            f.write("{}")
            data = {}
            f.close()
    return data

def writeData(channel_link: str, channel_name: str, who_to_mention: str, sendThumbnail: str, notifying_discord_channel: str):
    data = readData()

    if channel_link in data:
        data[channel_link][notifying_discord_channel] = {
            "channel_name": channel_name,
            "who_to_mention": who_to_mention,
            "latest_video_url": "",
            "latest_shorts_url": "",
            "latest_streams_url": "",
            "latest_upload_date": "",
            "sendThumbnail": sendThumbnail
        }
    else:
        data[channel_link] = {
            notifying_discord_channel: {
                "channel_name": channel_name,
                "who_to_mention": who_to_mention,
                "latest_video_url": "",
                "latest_shorts_url": "",
                "latest_streams_url": "",
                "latest_upload_date": "",
                "sendThumbnail": sendThumbnail
            }
        }

    with open(file_location, "w", encoding='utf-8') as f:
        json.dump(data, f, indent = 4)
        f.close()

