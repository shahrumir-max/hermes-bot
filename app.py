from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
from datetime import datetime
import threading

TOKEN = "8422008428:AAEVWsQKmZdG2Eh5bJkPx2cmL2yeioAOoqc"

app = Flask(__name__)

@app.route('/')
def home():
    return "ربات هرمس در حال اجرا است..."

# --- توابع ربات ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("سلام شهرام. من هرمس هستم.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("/weeklyplan - برنامه هفتگی\n/adderror - ثبت خطا")

# --- اجرای ربات ---
def run_bot():
    async def main():
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        await application.run_polling()

    asyncio.run(main())

if __name__ == '__main__':
    # اجرای ربات در یک Thread جداگانه
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # اجرای سرور Flask
    app.run(host='0.0.0.0', port=8080)
