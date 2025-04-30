import logging
import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
from memory import ConversationMemory

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
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

        # Добавляем сообщение пользователя в память
        memory.add_message(user_id, "user", user_message)

        # Получаем историю диалога
        conversation = memory.get_conversation(user_id)

        # Логируем запрос
        logging.info(f"Запрос к GPT: {conversation}")

        # Запрос к OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Обратите внимание на корректный формат модели
            messages=conversation
        )

        # Логируем ответ
        logging.info(f"Ответ от GPT: {response}")

        # Ответ ассистента
        reply = response["choices"][0]["message"]["content"]

        # Сохраняем ответ в память
        memory.add_message(user_id, "assistant", reply)

        # Отправляем ответ пользователю
        await update.message.reply_text(reply)

    except Exception as e:
        logging.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text("Произошла ошибка при обращении к GPT. Попробуй позже.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    port = int(os.getenv("PORT", 8000))
    print(f"Webhook URL: {WEBHOOK_URL}")
    print(f"Port: {os.getenv('PORT')}")
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()
