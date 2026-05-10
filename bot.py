import asyncio
asyncio.set_event_loop(asyncio.new_event_loop())

from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified
import os, requests, re, threading
from http.server import HTTPServer, BaseHTTPRequestHandler

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
bot_token = os.getenv("BOT_TOKEN")
worker_url = os.getenv("WORKER_URL")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    def log_message(self, *args):
        pass

def run_server():
    server = HTTPServer(("0.0.0.0", 10000), Handler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

app = Client("terabox_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

def get_download_link(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

        resp = requests.get(
            worker_url,
            params={"url": url},
            headers=headers,
            timeout=15
        )
        print("Response:", resp.status_code, resp.text[:300])

        if resp.status_code == 200 and resp.text.strip():
            data = resp.json()
            print("Data:", data)

            if data.get("errno") == 0:
                file_list = data.get("list", [])
                if file_list:
                    file = file_list[0]
                    return {
                        "name": file.get("server_filename", "TeraBox File"),
                        "size": int(file.get("size", 0)),
                        "dlink": file.get("dlink", ""),
                    }, None
                return None, "No files found"
            else:
                return None, f"Error {data.get('errno')}: {data.get('errmsg')}"
        else:
            return None, f"API returned: {resp.status_code}"

    except Exception as e:
        return None, f"Exception: {str(e)}"

def format_size(size):
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

@app.on_message(filters.text)
async def handler(_, m):
    if "terabox.com" not in m.text.lower() and "terabox.app" not in m.text.lower():
        return

    urls = re.findall(r'https?://[^\s]+terabox[^\s]+', m.text, re.IGNORECASE)
    if not urls:
        await m.reply("❌ Valid TeraBox link കണ്ടെത്തിയില്ല.")
        return

    msg = await m.reply("⏳ Processing your TeraBox link...")

    info, error = get_download_link(urls[0])

    if error:
        try:
            await msg.edit(f"❌ Failed: {error}")
        except MessageNotModified:
            pass
        return

    text = (
        f"📁 **{info['name']}**\n"
        f"📦 Size: {format_size(info['size'])}\n\n"
        f"⬇️ [Download Link]({info['dlink']})"
    )
    try:
        await msg.edit(text, disable_web_page_preview=True)
    except MessageNotModified:
        pass

if __name__ == "__main__":
    app.run()
