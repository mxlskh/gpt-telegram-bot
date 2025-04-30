
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from memory import ConversationMemory

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

logging.basicConfig(level=logging.INFO)

memory = ConversationMemory(max_messages=5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Осталось подключить чат GPT")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.chat.send_action(action="typing")
        user_message = update.message.text
        user_id = update.message.from_user.id

        memory.add_message(user_id, "user", user_message)

        # Заглушка: здесь должен быть ответ от OpenAI
        await update.message.reply_text("Ответ от GPT")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await update.message.reply_text("Произошла ошибка.")

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    port = int(os.getenv("PORT", 8000))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()
