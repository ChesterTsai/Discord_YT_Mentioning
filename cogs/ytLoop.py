import asyncio
import json
import requests
import re
import os
import discord
import datetime
from discord.ext import commands, tasks

file_location = "data/youtubedata.json"
REQUEST_TIMEOUT = 10  # 每個網頁請求的逾時秒數

class ytLoop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ytLoop.start()

    def cog_unload(self):
        self.ytLoop.cancel()

    @tasks.loop(seconds=30)
    async def ytLoop(self):
        try:
            data = readData()

            for youtube_channel in data:
                channel = youtube_channel
                discord_channel_id = data[str(youtube_channel)]

                for dc_id in discord_channel_id:
                    channel_name = data[youtube_channel][dc_id]["channel_name"]
                    who_to_mention = data[youtube_channel][dc_id]["who_to_mention"]
                    latest_upload_date = data[str(youtube_channel)][dc_id]["latest_upload_date"]
                    sendThumbnail = data[str(youtube_channel)][dc_id]["sendThumbnail"]

                    match who_to_mention:
                        case "everyone":
                            who_to_mention = "@everyone"
                        case "none":
                            who_to_mention = ""
                        case _:
                            who_to_mention = "<@&" + who_to_mention + ">"
                
                    # requests 是同步的，用 fetchText 丟到 thread 並行抓取，避免卡住整個機器人
                    try:
                        videos, shorts, streams, featured = await asyncio.gather(
                            fetchText(channel+"/videos"),
                            fetchText(channel+"/shorts"),
                            fetchText(channel+"/streams"),
                            fetchText(channel+"/featured"),
                        )

                        latest_video_url = "https://www.youtube.com/watch?v=" + re.search('(?<="videoId":").*?(?=")', videos).group()
                        latest_shorts_url = "https://www.youtube.com/shorts/" + re.search('(?<="videoId":").*?(?=")', shorts).group()
                        latest_streams_url = "https://www.youtube.com/live/" + re.search('(?<="videoId":").*?(?=")', streams).group()

                        latest_video_info, latest_shorts_info, latest_streams_info = await asyncio.gather(
                            fetchText(latest_video_url),
                            fetchText(latest_shorts_url),
                            fetchText(latest_streams_url),
                        )

                        video_upload_date = re.search('(?<="uploadDate":").*?(?=")', latest_video_info).group()
                        shorts_upload_date = re.search('(?<="uploadDate":").*?(?=")', latest_shorts_info).group()
                        stream_date = re.search('(?<="uploadDate":").*?(?=")', latest_streams_info).group()
                    except (AttributeError, requests.RequestException):
                        # 找不到資料或網路暫時失敗：這一輪跳過，下一輪再試
                        continue

                    # New Video Mentioning
                    if (str(data[youtube_channel][dc_id]["latest_video_url"]) != latest_video_url) and (video_upload_date > latest_upload_date):

                        msg = f"{who_to_mention} {channel_name}發布了新影片!\n"
                        msg += f"{channel_name} has uploaded a new video!\n"
                        if sendThumbnail == "y":
                            video_id = latest_video_url.split("https://www.youtube.com/watch?v=")
                            video_id = video_id[1]
                            thumbnail_url = "http://img.youtube.com/vi/%s/maxresdefault.jpg" % video_id
                            msg = msg + f"<{latest_video_url}>"
                            await self.bot.get_channel(int(dc_id)).send(msg)
                            await self.bot.get_channel(int(dc_id)).send(f"{thumbnail_url}")
                        else:
                            msg = msg + f"{latest_video_url}"
                            await self.bot.get_channel(int(dc_id)).send(msg)

                        # 訊息送出成功之後才記錄，送失敗的話下一輪還會再通知
                        updateEntry(youtube_channel, dc_id,
                                    latest_upload_date = video_upload_date,
                                    latest_video_url = latest_video_url)

                        print(f'[{datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")} INFO] New Video Info Sent!')

                    # Skip Shorts Mentioning if the page don't have shorts
                    video_id = latest_video_url.split("https://www.youtube.com/watch?v=")
                    video_id = video_id[1]
                    shorts_id = latest_shorts_url.split("https://www.youtube.com/shorts/")
                    shorts_id = shorts_id[1]
                    if video_id != shorts_id:

                        # New Shorts Mentioning
                        if (str(data[youtube_channel][dc_id]["latest_shorts_url"]) != latest_shorts_url) and (shorts_upload_date > latest_upload_date):

                            msg = f"{who_to_mention} {channel_name}發布了新的shorts!\n"
                            msg += f"{channel_name} has uploaded a new short!\n{latest_shorts_url}"

                            await self.bot.get_channel(int(dc_id)).send(msg)
                            updateEntry(youtube_channel, dc_id,
                                        latest_upload_date = shorts_upload_date,
                                        latest_shorts_url = latest_shorts_url)

                            print(f'[{datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")} INFO] New Shorts Info Sent!')

                    # Skip Streams Mentioning if the page don't have streams
                    featured_match = re.search('(?<="videoId":").*?(?=")', featured)
                    featured_id = featured_match.group() if featured_match else None
                    streams_id = latest_streams_url.split("https://www.youtube.com/live/")
                    streams_id = streams_id[1]
                    # 精選頁找不到影片時無法判斷，這一輪先跳過直播通知
                    if featured_id is not None and featured_id != streams_id:

                        # New Streams Mentioning
                        if (str(data[youtube_channel][dc_id]["latest_streams_url"]) != latest_streams_url) and (stream_date > latest_upload_date):

                            msg = f"{who_to_mention} {channel_name}開台了!\n"
                            msg += f"{channel_name} has went on live!\n{latest_streams_url}"

                            await self.bot.get_channel(int(dc_id)).send(msg)
                            updateEntry(youtube_channel, dc_id,
                                        latest_upload_date = stream_date,
                                        latest_streams_url = latest_streams_url)

                            print(f'[{datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")} INFO] New Streams Info Sent!')
        except Exception as e:
            import traceback
            traceback.print_exception(e)
            raise e


    @ytLoop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()
    
async def setup(bot):
    await bot.add_cog(ytLoop(bot))

async def fetchText(url):
    # requests 是同步的，丟到 thread 執行才不會卡住 event loop；加上逾時避免無限等待
    response = await asyncio.to_thread(requests.get, url, timeout = REQUEST_TIMEOUT)
    return response.text

def saveJson(data):
    # 先寫到暫存檔再替換，避免寫到一半當機而弄壞 json
    tmpPath = file_location + ".tmp"
    with open(tmpPath, "w", encoding='utf-8') as f:
        json.dump(data, f, indent = 4)
    os.replace(tmpPath, file_location)

def updateEntry(channel_link, discord_channel_id, **fields):
    # 重新讀檔、只改這一筆再寫回，不會蓋掉 Loop 執行期間其他指令新增或修改的資料
    # （讀和寫之間沒有 await，所以不會被其他指令穿插）
    data = readData()
    entry = data.get(channel_link, {}).get(discord_channel_id)
    if entry is None:
        return  # 這一筆已經被移除了
    entry.update(fields)
    saveJson(data)

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

    saveJson(data)
