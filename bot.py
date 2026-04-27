import json
import logging
import os
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
FILE = "birthdays.json"

logging.basicConfig(level=logging.INFO)

# ------------------ Работа с файлом ------------------

def load_data():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ------------------ Команды ------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 Я бот дней рождения!\n\n"
        "/add Имя ДД-ММ\n"
        "/list\n"
        "/delete Имя"
    )

# ➕ Добавить
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name = context.args[0]
        date = context.args[1]

        # проверка формата
        datetime.strptime(date, "%d-%m")

        data = load_data()
        data[name] = date
        save_data(data)

        await update.message.reply_text(f"✅ Добавлено: {name} — {date}")

    except:
        await update.message.reply_text("❌ Используй: /add Имя ДД-ММ")

# 📋 Список
async def list_birthdays(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()

    if not data:
        await update.message.reply_text("📭 Список пуст")
        return

    text = "📋 Дни рождения:\n\n"
    for name, date in data.items():
        text += f"{name} — {date}\n"

    await update.message.reply_text(text)

# ❌ Удалить
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name = context.args[0]

        data = load_data()

        if name in data:
            del data[name]
            save_data(data)
            await update.message.reply_text(f"🗑 Удалено: {name}")
        else:
            await update.message.reply_text("❌ Не найдено")

    except:
        await update.message.reply_text("❌ Используй: /delete Имя")

# 🎉 Проверка дней рождения
async def check_birthdays(context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    today = datetime.now().strftime("%d-%m")

    for name, date in data.items():
        if date == today:
            message = f"""
🎉🎂 УРААА!!! 🎂🎉

Сегодня день рождения у {name}!

✨ Счастья
💰 Денег
❤️ Любви
🚀 Успехов!

С ДНЁМ РОЖДЕНИЯ!!! 🥳
"""
            await context.bot.send_message(
                chat_id=context.job.chat_id,
                text=message
            )

# ------------------ Запуск ------------------

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_birthdays))
    app.add_handler(CommandHandler("delete", delete))

    # ежедневная проверка
    app.job_queue.run_daily(
        check_birthdays,
        time=datetime.now().time(),
        chat_id=123456789  # ВСТАВЬ СВОЙ CHAT_ID
    )

    print("Бот запущен...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
