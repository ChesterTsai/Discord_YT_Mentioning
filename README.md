# token.txt
運行這個機器人前，需要建立一個"token.txt"文件，並把機器人TOKEN寫進去<br>
Before running this bot, you need to create a "token.txt" file, and write the Discord Bot Token in it.

# 機器人邀請連結 - Bot Invite Link:<br>
https://discordapp.com/api/oauth2/authorize?client_id=1248612928601722971&permissions=8&scope=bot <br>

# "youtubedata.json"的格式 - format in "youtubedata.json" <br>
{ <br>
&emsp;	"(Youtube帳號代碼 - Youtube Handle)": <br>
&emsp;&emsp;	{ <br>
&emsp;&emsp;	"channel_name": "(想寫什麼都可以 - write what ever you want)", <br>
<br>
&emsp;&emsp;	"who_to_mention": "(everyone / none / roleID)", <br>
// everyone -> @everyone <br>
none -> 單純文字通知 - plain text mention <br>
roleID -> 通知該身分組，填上discord身分組ID - mention specific role, insert discord role ID <br>
<br>
&emsp;&emsp;	"latest_video_url": "(會自行偵測，不必填寫 - it'll detect itself, you can leave it blank)", <br>
&emsp;&emsp;	"latest_shorts_url": "(會自行偵測，不必填寫 - it'll detect itself, you can leave it blank)", <br>
&emsp;&emsp;	"notifying_discord_channel": "(discord頻道ID - discord Channel ID)" <br>
&emsp;&emsp;	} <br>
} <br>

### Example:
{ <br>
&emsp;	"chester1023": <br>
&emsp;&emsp;	{ <br>
&emsp;&emsp;	"channel_name": "口才才口", <br>
&emsp;&emsp;	"who_to_mention": "none", <br>
&emsp;&emsp;	"latest_video_url": "", <br>
&emsp;&emsp;	"latest_shorts_url": "", <br>
&emsp;&emsp;	"notifying_discord_channel": "1310097305785077853" <br>
&emsp;&emsp;	} <br>
} <br>
