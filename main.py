import os
import requests
import time
import asyncio
from urllib.parse import urlparse, urlunparse
from pyrogram import Client, filters

# --- CONFIGURATION ---
# Railway/Render Environment Variables-il ninnu values edukkunnu
API_ID = int(os.environ.get("API_ID", "your_api_id"))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

# Authorized Group ID
AUTH_CHAT = -1003909593261

app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# API Endpoint
API_URL = "https://silent-noor-stream-api.woodmirror.workers.dev/api?url="

# Supported TeraBox Domains
TERABOX_DOMAINS = [
    "terabox.app", "teraboxshare.com", "terabox.com", 
    "1024terabox.com", "teraboxlink.com", "terasharefile.com", 
    "terafileshare.com", "terasharelink.com"
]

def format_url(original_url):
    """Domain-ine 1024terabox.com-lekk force convert cheyyunnu"""
    parsed = urlparse(original_url)
    # Hostname matram 1024terabox.com aakkunnu
    new_url = urlunparse((
        parsed.scheme, 
        "1024terabox.com", 
        parsed.path, 
        parsed.params, 
        parsed.query, 
        parsed.fragment
    ))
    return new_url

@app.on_message(filters.command("start") & filters.chat(AUTH_CHAT))
async def start(client, message):
    await message.reply_text("TeraBox Downloader Bot ready! Link ayakkuka. 🚀")

@app.on_message(filters.text & filters.chat(AUTH_CHAT))
async def handle_terabox(client, message):
    url = message.text.strip()
    
    # Check if the message contains a valid TeraBox domain
    is_terabox = any(domain in url for domain in TERABOX_DOMAINS)
    if not is_terabox:
        return

    status = await message.reply_text("🔎 `Processing and Converting...`", quote=True)

    try:
        # Link transform cheyyunnu (API compatibility-nu vendi)
        final_url = format_url(url)
        
        # API-lekk converted link ayakkunnu
        res = requests.get(f"{API_URL}{final_url}").json()
        
        if res.get("status") != "✅ Successfully":
            await status.edit("❌ API Error: Data fetch cheyyan kazhinjilla.")
            return

        file_name = res.get("file_name")
        download_url = res.get("download_link")
        file_size = res.get("file_size")
        
        await status.edit(f"📥 `Downloading: {file_name}`\n`Size: {file_size}`")

        # Local path for temporary storage
        path = f"{time.time()}_{file_name}"

        # Download with chunking to save RAM
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)

        await status.edit("📤 `Uploading to Telegram...`")

        # Telegram-ilekk upload cheyyunnu
        await message.reply_document(
            document=path,
            caption=f"**File:** `{file_name}`\n**Size:** `{file_size}`",
            quote=True
        )

        # Cleanup: Local file delete cheyyunnu
        if os.path.exists(path):
            os.remove(path)
        await status.delete()

    except Exception as e:
        await status.edit(f"❌ Error: {str(e)}")
        if 'path' in locals() and os.path.exists(path):
            os.remove(path)

print("Bot is starting in Authorized Group...")
app.run()
