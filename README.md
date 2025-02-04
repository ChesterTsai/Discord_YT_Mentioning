# Prerequisites
運行`pip3 install -r requirements.txt`來下載所需的程序依賴<br>
run `pip3 install -r requirements.txt` to install required dependencies<br>
<br>
運行這個機器人前，需要建立一個"token.txt"文件，並把機器人TOKEN寫進去<br>
Before running this bot, you need to create a "token.txt" file, and write the Discord Bot Token in it.

# 機器人邀請連結 - Bot Invite Link:<br>
https://discordapp.com/api/oauth2/authorize?client_id=1248612928601722971&permissions=8&scope=bot <br>

# "youtubedata.json"的格式 - format in "youtubedata.json" <br>
```Json
{
  "(Youtube帳號代碼 - Youtube Handle)":
    {
      "channel_name": "(想寫什麼都可以 - write what ever you want)",

      "who_to_mention": "(everyone / none / roleID)",

//      everyone -> @everyone
        none -> 單純文字通知 - plain text mention
        roleID -> 通知該身分組，填上discord身分組ID - mention specific role, insert discord role ID

      "latest_video_url": "(會自行偵測，不必填寫 - it'll detect itself, you can leave it blank)",
      "latest_shorts_url": "(會自行偵測，不必填寫 - it'll detect itself, you can leave it blank)",
      "notifying_discord_channel": "(discord頻道ID - discord Channel ID)"
    }
}
```

### Example:
```Json
{
  "chester1023":
    {
      "channel_name": "口才才口",
      "who_to_mention": "everyone",
      "latest_video_url": "",
      "latest_shorts_url": "",
      "notifying_discord_channel": "1310097305785077853"
    }
}
```
