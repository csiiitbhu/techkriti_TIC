from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import logging
import json
import re
import hashlib
import asyncio

logging.basicConfig(level=logging.INFO)

TOKEN = "8672858511:AAEgGzzO5gdzgLxUkWk0-iZ4UjA5yHhOJp8"  # ⚠️ Replace with new token

# 📦 Global buffer
message_buffer = []
processing = False


# 🔥 Batch processor
async def process_buffer():
    global message_buffer, processing

    await asyncio.sleep(5)  # ⏳ wait to collect messages

    batch = message_buffer.copy()
    message_buffer = []
    processing = False

    print(f"📦 Processing {len(batch)} messages together")

    # 📁 Save JSON
    try:
        with open("messages.json", "r") as file:
            existing_data = json.load(file)
    except:
        existing_data = []

    existing_data.extend(batch)

    with open("messages.json", "w") as file:
        json.dump(existing_data, file, indent=4)

    print("✅ Batch saved successfully")


# 📩 Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global message_buffer, processing

    if not update.message:
        return

    msg = update.message
    user_obj = msg.from_user

    # 🧑 User Info
    user_id = user_obj.id
    username = user_obj.username
    first_name = user_obj.first_name
    last_name = user_obj.last_name
    name = username if username else f"{first_name} {last_name or ''}".strip()

    # ⏰ Time
    timestamp = msg.date.strftime("%Y-%m-%d %H:%M:%S")

    # 💬 Message
    text = msg.text if msg.text else ""

    # 🔗 Links detection
    links = re.findall(r'https?://\S+', text)
    contains_link = bool(links)

    # 🧬 Message hash
    msg_hash = hashlib.md5(text.encode()).hexdigest()

    # 🔁 Forward source check
    forwarded = False
    forward_from = None

    if msg.forward_origin:
        forwarded = True
        forward_from = str(msg.forward_origin)

    # 💬 Chat info
    chat_id = msg.chat.id
    chat_type = msg.chat.type

    print("🔥 Message received:", text)

    # 📦 Data object
    data = {
        "user_id": user_id,
        "username": username,
        "name": name,
        "message": text,
        "timestamp": timestamp,
        "chat_id": chat_id,
        "chat_type": chat_type,
        "contains_link": contains_link,
        "links": links,
        "message_hash": msg_hash,
        "forwarded": forwarded,
        "forward_source": forward_from
    }

    # ➕ Add to buffer
    message_buffer.append(data)

    # 🚀 Start batch processing
    if not processing:
        processing = True
        asyncio.create_task(process_buffer())

    # Optional reply (remove if spam)
    await msg.reply_text("📥 Message queued")


# 🚀 Run bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, handle_message))

print("🚀 Bot is starting...")
app.run_polling()