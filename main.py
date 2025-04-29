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
openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

memory = ConversationMemory(max_messages=5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Скорее всего сосать, но все же попробуй написать еще что-нибудь")



async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
   try:
    await update.message.chat.send_action(action="typing")  # "набирает сообщение..."
    user_message = update.message.text
    user_id = update.message.from_user.id

    memory.add_message(user_id, "user", user_message)

    conversation = memory.get_conversation(user_id)
    messages = [{"role": role, "content": content} for role, content in conversation]
    messages.insert(0, {
    "role": "system",
    "content": (
        "Ты — Telegram-бот на базе ChatGPT, созданный специально для репетиторов по иностранным языкам. "
        "Ты помогаешь готовить материалы к урокам, проверять письменные задания, придумывать упражнения под уровень ученика, "
        "переводить тексты, давать грамматические пояснения — всё в одном чате, без копипасты. "
        "Сократи рутину и помоги преподавателю сосредоточиться на обучении. "
        "Отвечай понятно, профессионально, с фокусом на практическую пользу для преподавателя."
    )
})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
        temperature=0.7,
        max_tokens=500,
    )

    bot_reply = response['choices'][0]['message']['content']
    memory.add_message(user_id, "assistant", bot_reply)

    await update.message.reply_text(bot_reply)

     except Exception as e:
        logging.error(f"Ошибка при обращении к OpenAI: {e}")
        await update.message.reply_text("Произошла ошибка при работе с ИИ. Попробуй позже.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()
