import logging
from telegram import Update, Message, ChatAction
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# List of emojis to react with
EMOJIS = ["🔥", "😂", "❤️", "👍", "😎"]

async def auto_react(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    msg: Message = update.message
    user = msg.from_user

    # Send a typing action
    await context.bot.send_chat_action(chat_id=msg.chat_id, action=ChatAction.TYPING)

    # 1. React with emoji (reply with random emoji or fixed)
    emoji = EMOJIS[hash(user.id) % len(EMOJIS)]  # Random but consistent per user
    await msg.reply_text(f"{emoji}")

    # 2. Clone/echo the original message (text, photo, etc.)
    if msg.text:
        await msg.reply_text(f"Echo: {msg.text}")
    elif msg.photo:
        file_id = msg.photo[-1].file_id
        await msg.reply_photo(photo=file_id, caption="Echo: Photo")
    elif msg.video:
        await msg.reply_video(video=msg.video.file_id, caption="Echo: Video")
    elif msg.sticker:
        await msg.reply_sticker(sticker=msg.sticker.file_id)
    else:
        await msg.reply_text("Echo: I received something cool!")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling update:", exc_info=context.error)

def main():
    import os
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise Exception("BOT_TOKEN environment variable not set.")

    app = ApplicationBuilder().token(TOKEN).build()

    # Register handler for all message types
    app.add_handler(MessageHandler(filters.ALL, auto_react))
    app.add_error_handler(error_handler)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
