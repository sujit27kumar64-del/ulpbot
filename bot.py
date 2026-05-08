import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8729991262:AAFUfXGHaX9Adw9O02M008f8IKukVhhw4fs"

user_data_store = {}

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📂 Send txt/log/combo files.\n"
        "Then use:\n\n"
        "/keyword netflix\n\n"
        "Bot will search and send matched results."
    )

# ===== RECEIVE FILES =====
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id

    if user_id not in user_data_store:
        user_data_store[user_id] = {
            "files": [],
            "keyword": None
        }

    document = update.message.document

    file = await context.bot.get_file(document.file_id)

    folder = f"downloads/{user_id}"

    os.makedirs(folder, exist_ok=True)

    path = os.path.join(folder, document.file_name)

    await file.download_to_drive(path)

    user_data_store[user_id]["files"].append(path)

    await update.message.reply_text(
        f"✅ File Saved:\n{document.file_name}"
    )

# ===== SET KEYWORD =====
async def keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id

    if len(context.args) == 0:
        await update.message.reply_text(
            "Usage:\n/keyword netflix"
        )
        return

    keyword = " ".join(context.args).lower()

    if user_id not in user_data_store or not user_data_store[user_id]["files"]:
        await update.message.reply_text(
            "❌ First send files."
        )
        return

    files = user_data_store[user_id]["files"]

    matched = set()

    output_file = f"matched_{user_id}.txt"

    found = 0

    await update.message.reply_text(
        f"🔍 Searching for: {keyword}"
    )

    with open(output_file, "w", encoding="utf-8") as out:

        for file_path in files:

            try:

                with open(file_path, "rb") as f:

                    for raw_line in f:

                        try:
                            line = raw_line.decode(
                                "utf-8",
                                errors="ignore"
                            ).strip()

                        except:
                            continue

                        if keyword in line.lower():

                            if line in matched:
                                continue

                            matched.add(line)

                            out.write(line + "\n")

                            found += 1

            except:
                pass

    if found == 0:
        await update.message.reply_text(
            "❌ No matching lines found."
        )
        return

    await update.message.reply_text(
        f"✅ Found: {found}\n📤 Sending file..."
    )

    await update.message.reply_document(
        document=open(output_file, "rb")
    )

# ===== RUN =====
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("keyword", keyword))
app.add_handler(
    MessageHandler(filters.Document.ALL, handle_document)
)

print("Bot Running...")

app.run_polling()