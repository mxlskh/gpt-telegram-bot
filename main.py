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
    await update.message.reply_text(
    "Привет! Я — бот, который поможет в изучении иностранных языков.\n"
    "Я создан для того, чтобы поддерживать преподавателей и учеников на каждом этапе обучения:\n\n"
    "👩‍🏫 Я помогу преподавателю:\n"
    "• быстро создавать задания, тексты и упражнения\n"
    "• объяснять грамматику простым языком\n"
    "• проверять письменные работы и давать обратную связь\n"
    "• готовить к экзаменам, таким как IELTS или TOEFL\n"
    "• избавляться от рутины — чтобы вы занимались только преподаванием\n\n"
    "👨‍🎓 Я помогу ученику:\n"
    "• понять сложные темы и правила\n"
    "• потренировать письмо, говорение, чтение\n"
    "• получить комментарии к своим эссе и ответам\n"
    "• готовиться к реальным заданиям и экзаменам\n\n"
    "💡 Я могу работать в разных режимах — просто нажми 'меню' выбери нужный:"
)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.chat.send_action(action="typing")
        user_message = update.message.text
        user_id = update.message.from_user.id

        memory.add_message(user_id, "user", user_message)

        conversation = memory.get_conversation(user_id)

        logging.info(f"Запрос к GPT: {conversation}")

        response = openai.ChatCompletion.create(
            model="gpt-3.5turbo",  # Обратите внимание на корректный формат модели
            messages=conversation
        )
        logging.info(f"Ответ от GPT: {response}")

        reply = response["choices"][0]["message"]["content"]

        memory.add_message(user_id, "assistant", reply)

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
