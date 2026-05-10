import os
import requests
import time
import asyncio
from pyrogram import Client, filters

# Environment Variables
API_ID = int(os.environ.get("API_ID", "12345"))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

API_URL = "https://silent-noor-stream-api.woodmirror.workers.dev/api?url="

# Ningal paranja ella domains-um oru list-ilekk
TERABOX_DOMAINS = [
    "terabox.app", "teraboxshare.com", "terabox.com", 
    "1024terabox.com", "teraboxlink.com", "terasharefile.com", 
    "terafileshare.com", "terasharelink.com"
]

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("TeraBox link ayakkuka, njan athu download cheythu tharaam! 🚀")

@app.on_message(filters.text & filters.private)
async def handle_terabox(client, message):
    url = message.text.strip()
    
    # Check if the domain is in our list
    is_terabox = any(domain in url for domain in TERABOX_DOMAINS)
    
    if not is_terabox:
        return

    status = await message.reply_text("🔎 `Fetching details...`", quote=True)

    try:
        # API Request
        res = requests.get(f"{API_URL}{url}").json()
        if res.get("status") != "✅ Successfully":
            await status.edit("❌ Error: Link valid alla ennu thonnunnu or API down aanu.")
            return

        file_name = res.get("file_name")
        download_url = res.get("download_link")
        
        await status.edit(f"📥 `Downloading: {file_name}`")

        # Local Path for Railway
        path = f"{time.time()}_{file_name}"

        # Download logic
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    f.write(chunk)

        await status.edit("📤 `Uploading to Telegram...`")

        # Uploading
        await message.reply_document(
            document=path,
            caption=f"**File:** `{file_name}`\n**Size:** {res.get('file_size')}",
            quote=True
        )

        # Cleanup
        if os.path.exists(path):
            os.remove(path)
        await status.delete()

    except Exception as e:
        await status.edit(f"❌ Error: {str(e)}")
        if 'path' in locals() and os.path.exists(path):
            os.remove(path)

print("Bot is starting...")
app.run()
