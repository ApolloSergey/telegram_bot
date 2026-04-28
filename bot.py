import json
import logging
import os
import threading
import time
import pytz
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import time
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
FILE = "birthdays.json"

# 🔥 ТВОЙ URL (у тебя уже правильный)
KEEP_ALIVE_URL = "https://telegram-bot-y750.onrender.com"

logging.basicConfig(level=logging.INFO)

# ------------------ KEEP ALIVE ------------------

def keep_alive():
    while True:
        try:
            requests.get(KEEP_ALIVE_URL)
            print("Ping server...")
        except Exception as e:
            print("Ping error:", e)

        time.sleep(600)  # каждые 10 минут

# ------------------ HTTP сервер (ИСПРАВЛЕН) ------------------

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    # убираем спам логов
    def log_message(self, format, *args):
        return

def run_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Web server running on {port}")
    server.serve_forever()

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

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name = context.args[0]
        date = context.args[1]

        datetime.strptime(date, "%d-%m")

        data = load_data()
        data[name] = date
        save_data(data)

        await update.message.reply_text(f"✅ Добавлено: {name} — {date}")

    except:
        await update.message.reply_text("❌ Используй: /add Имя ДД-ММ")

async def list_birthdays(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()

    if not data:
        await update.message.reply_text("📭 Список пуст")
        return

    text = "📋 Дни рождения:\n\n"
    for name, date in data.items():
        text += f"{name} — {date}\n"

    await update.message.reply_text(text)

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

# ------------------ Проверка дней рождения ------------------

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

# ------------------ ЗАПУСК ------------------

def main():
    threading.Thread(target=run_web, daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_birthdays))
    app.add_handler(CommandHandler("delete", delete))

    # ⏰ запуск каждый день в 12:00
    
    app.job_queue.run_daily(
    check_birthdays,
    time=time(hour=12, minute=0, tzinfo=pytz.timezone("Europe/Luxembourg")),
    chat_id=123456789
    )
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
