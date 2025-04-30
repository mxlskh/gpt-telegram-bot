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

openai.api_key = OPENAI_API_KEY
logging.basicConfig(level=logging.INFO)

memory = ConversationMemory(max_messages=5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я ассистент для преподавателей английского. Напиши мне или выбери режим:\n/mode_ielts\n/mode_grammar\n/mode_reset")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.chat.send_action(action="typing")
        user_message = update.message.text
        user_id = update.message.from_user.id

        # Добавляем сообщение пользователя в память
        memory.add_message(user_id, "user", user_message)

        # Получаем историю диалога
        conversation = memory.get_conversation(user_id)
        messages = [{"role": role, "content": content} for role, content in conversation]

        # Получаем режим пользователя
        mode = context.user_data.get("mode", None)

        if mode == "ielts":
            system_prompt = (
                "Ты — персональный ассистент преподавателя по подготовке к IELTS. "
                "Ты создаёшь задания, оцениваешь письменные ответы по критериям IELTS, "
                "даёшь обратную связь и помогаешь с материалами для подготовки."
            )
        elif mode == "grammar":
            system_prompt = (
                "Ты — ассистент по грамматике английского языка. "
                "Ты объясняешь правила, исправляешь ошибки и создаёшь упражнения."
            )
        else:
            system_prompt = (
                "Ты — универсальный помощник преподавателя английского. "
                "Ты помогаешь с упражнениями, объяснениями и подбором материалов для уроков."
            )

        messages.insert(0, {"role": "system", "content": system_prompt})

        # Логируем запрос
        logging.info(f"Запрос к GPT: {messages}")

        # Запрос к OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
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

# Команды смены режима
async def set_mode_ielts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "ielts"
    await update.message.reply_text("✅ Режим IELTS активирован.")

async def set_mode_grammar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "grammar"
    await update.message.reply_text("✅ Режим грамматики активирован.")

async def reset_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = None
    await update.message.reply_text("🔁 Режим сброшен. Используется общий помощник.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mode_ielts", set_mode_ielts))
    app.add_handler(CommandHandler("mode_grammar", set_mode_grammar))
    app.add_handler(CommandHandler("mode_reset", reset_mode))
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
