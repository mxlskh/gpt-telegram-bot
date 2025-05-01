import logging
import os
import openai
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)
from dotenv import load_dotenv
from memory import ConversationMemory

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

openai.api_key = OPENAI_API_KEY
logging.basicConfig(level=logging.INFO)

memory = ConversationMemory(max_messages=5)

# States
SELECT_ROLE, SELECT_LANGUAGE, SELECT_GOAL = range(3)

roles = ["Преподаватель", "Ученик"]
languages = ["Английский", "Немецкий", "Французский", "Китайский"]
student_goals = ["Грамматика", "Аудирование", "Чтение", "Прослушивание"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я — бот, который поможет в изучении иностранных языков.\n"
        "Используй команду /menu, чтобы начать."
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton(role)] for role in roles]
    await update.message.reply_text(
        "Кто вы?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return SELECT_ROLE

async def select_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = update.message.text
    context.user_data["role"] = role
    keyboard = [[KeyboardButton(lang)] for lang in languages]
    await update.message.reply_text(
        f"Вы выбрали: {role}. Какой язык вас интересует?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return SELECT_LANGUAGE

async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = update.message.text
    context.user_data["language"] = language

    role = context.user_data.get("role")
    if role == "Ученик":
        keyboard = [[KeyboardButton(goal)] for goal in student_goals]
        await update.message.reply_text(
            f"Вы выбрали язык: {language}. Что вы хотите изучать?",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return SELECT_GOAL
    else:
        await update.message.reply_text(
            f"Вы выбрали: Преподаватель по языку {language}. Я помогу вам готовить материалы и проверять задания.",
            reply_markup=None
        )
        return ConversationHandler.END

async def select_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goal = update.message.text
    context.user_data["goal"] = goal
    await update.message.reply_text(
        f"Отлично! Вы ученик. Язык: {context.user_data['language']}. Цель: {goal}.",
        reply_markup=None
    )
    return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.chat.send_action(action="typing")
        user_message = update.message.text
        user_id = update.message.from_user.id

        memory.add_message(user_id, "user", user_message)
        conversation = memory.get_conversation(user_id)

        logging.info(f"Запрос к GPT: {conversation}")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation
        )

        reply = response["choices"][0]["message"]["content"]
        memory.add_message(user_id, "assistant", reply)

        await update.message.reply_text(reply)

    except Exception as e:
        logging.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text("Произошла ошибка при обращении к GPT. Попробуй позже.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("menu", menu)],
        states={
            SELECT_ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_role)],
            SELECT_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_language)],
            SELECT_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_goal)]
        },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
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
