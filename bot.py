import os
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import Message

# --- Environment variables ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7931367906:AAEM8Rjfg9V8OW3jVAlNGWRHXpdcyNagdm4")
API_ID = int(os.environ.get("API_ID", "23340285"))
API_HASH = os.environ.get("API_HASH", "ab18f905cb5f4a75d41bb48d20acfa50")

# --- Client setup ---
APP = Client("cover_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# --- Database setup ---
conn = sqlite3.connect("covers.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS covers (
    chat_id INTEGER PRIMARY KEY,
    file_id TEXT NOT NULL
)
""")
conn.commit()


# --- Helper functions ---
def save_cover(chat_id: int, file_id: str):
    cur.execute("REPLACE INTO covers(chat_id, file_id) VALUES (?, ?)", (chat_id, file_id))
    conn.commit()

def get_cover(chat_id: int):
    cur.execute("SELECT file_id FROM covers WHERE chat_id = ?", (chat_id,))
    result = cur.fetchone()
    return result[0] if result else None

def delete_cover(chat_id: int):
    cur.execute("DELETE FROM covers WHERE chat_id = ?", (chat_id,))
    conn.commit()


# --- Commands ---
@APP.on_message(filters.command("start"))
async def start(_, m: Message):
    await m.reply_text(
        "🎬 **Welcome to Video Cover/Thumbnail Bot!**\n\n"
        "☞ Send me a **photo** to set as cover.\n"
        "☞ Then send a **video**, I’ll apply your cover automatically.\n\n"
        "**Commands:**\n"
        "/show_cover - Show saved cover\n"
        "/del_cover - Delete saved cover"
    )


# --- Photo received ---
@APP.on_message(filters.photo)
async def photo_handler(_, m: Message):
    save_cover(m.chat.id, m.photo.file_id)
    await m.reply_text("✅ Cover/Thumbnail Saved Successfully")


# --- Show cover ---
@APP.on_message(filters.command("show_cover"))
async def show_cover(_, m: Message):
    cover = get_cover(m.chat.id)
    if not cover:
        return await m.reply_text("❌ No cover saved yet.")
    await m.reply_photo(cover, caption="✅ Saved Cover")


# --- Delete cover ---
@APP.on_message(filters.command("del_cover"))
async def del_cover(_, m: Message):
    delete_cover(m.chat.id)
    await m.reply_text("🗑️ Cover deleted successfully.")


# --- Video received ---
@APP.on_message(filters.video | filters.document)
async def video_handler(_, m: Message):
    cover = get_cover(m.chat.id)
    if not cover:
        return await m.reply_text("❌ No cover saved. Send a photo first.")

    video = m.video or m.document
    await m.reply_text("⏳ Applying saved cover...")
    try:
        await APP.send_video(
            m.chat.id,
            video=video.file_id,
            thumb=cover,
            caption="✅ Cover applied successfully!",
            supports_streaming=True
        )
        await m.reply_text("Done ✅")
    except Exception as e:
        await m.reply_text(f"⚠️ Error while applying cover:\n{e}")


print("Bot Started Successfully ✅")
APP.run()
