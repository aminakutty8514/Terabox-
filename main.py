import os
import requests
from urllib.parse import urlparse, urlunparse
from pyrogram import Client, filters

# Setup (API_ID, HASH, TOKEN)
API_ID = int(os.environ.get("API_ID", "12345"))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# API endpoint
API_URL = "https://silent-noor-stream-api.woodmirror.workers.dev/api?url="

# Supported domains for checking
SUPPORTED_TERABOX = [
    "terabox.app", "teraboxshare.com", "terabox.com", 
    "1024terabox.com", "teraboxlink.com", "terasharefile.com", 
    "terafileshare.com", "terasharelink.com"
]

def convert_to_1024(original_url):
    """
    User ayakkunna link-ile domain maatti '1024terabox.com' aakkunnu
    """
    parsed = urlparse(original_url)
    # Domain-ine 1024terabox.com aayi replace cheyyunnu
    new_netloc = "1024terabox.com"
    new_url = urlunparse((parsed.scheme, new_netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
    return new_url

@app.on_message(filters.text & filters.private)
async def handle_terabox(client, message):
    url = message.text.strip()
    
    # URL-il TeraBox undo ennu check cheyyunnu
    if not any(domain in url for domain in SUPPORTED_TERABOX):
        return

    status = await message.reply_text("🔄 `Converting and Fetching...`", quote=True)

    try:
        # Link-ine 1024terabox.com format-ilekk maattunnu
        final_url = convert_to_1024(url)
        
        # API Request
        res = requests.get(f"{API_URL}{final_url}").json()
        
        if res.get("status") != "✅ Successfully":
            await status.edit("❌ API Error: Link process cheyyan kazhinjilla.")
            return

        # Download & Upload logic
        file_url = res.get("download_link")
        file_name = res.get("file_name")
        
        await status.edit(f"📥 `Downloading: {file_name}`")
        
        # Download...
        path = f"./{file_name}"
        with requests.get(file_url, stream=True) as r:
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    f.write(chunk)
                    
        await status.edit("📤 `Uploading...`")
        await message.reply_document(document=path, quote=True)
        
        # Cleanup
        os.remove(path)
        await status.delete()

    except Exception as e:
        await status.edit(f"❌ Error: {str(e)}")

app.run()
