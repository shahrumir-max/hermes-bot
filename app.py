import os
import sqlite3
import asyncio
import threading
from datetime import datetime
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- تنظیمات ---
TOKEN = "8422008428:AAEVWsQKmZdG2Eh5bJkPx2cmL2yeioAOoqc"
DB_NAME = "hermes.db"

# --- دیتابیس ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS weekly_plans (user_id INTEGER, plan_text TEXT, date TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS errors (user_id INTEGER, error_text TEXT, date TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS achievements (user_id INTEGER, achievement_text TEXT, date TEXT)''')
    conn.commit()
    conn.close()

# --- توابع کمکی ---
async def send_md_file(update: Update, context: ContextTypes.DEFAULT_TYPE, filename: str):
    file_path = os.path.join('content', filename)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        # تقسیم متن به بخش‌های 3800 کاراکتری برای جلوگیری از خطای تلگرام
        for i in range(0, len(text), 3800):
            await update.message.reply_text(text[i:i+3800])
    else:
        await update.message.reply_text(f"فایل {filename} پیدا نشد. لطفاً آن را در پوشه content گیت‌هاب بسازید.")

# --- دستورات ربات ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
سلام شهرام. من هرمس هستم. دستیار معاملات فارکس شما.

دستورات موجود:
/weeklyplan - تنظیم برنامه هفتگی
/dailycheck - چک‌لیست شروع بازار روزانه
/pretrade - چک‌لیست قبل از ترید
/adderror - ثبت خطای معاملاتی
/addachievement - ثبت دستاورد
/showerrors - نمایش خطاها
/showachievements - نمایش دستاوردها
/checklist - مشاهده چک‌لیست استراتژی
/strategy - مشاهده استراتژی معاملاتی
/weeklyreview - مشاهده بررسی هفتگی
/help - راهنمایی
"""
    await update.message.reply_text(message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start_command(update, context)

async def weekly_plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if context.args:
        plan = ' '.join(context.args)
        date = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO weekly_plans (user_id, plan_text, date) VALUES (?, ?, ?)", (user_id, plan, date))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"✅ برنامه هفتگی ثبت شد:\n\n{plan}")
    else:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT plan_text FROM weekly_plans WHERE user_id=? ORDER BY rowid DESC LIMIT 1", (user_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            await update.message.reply_text(f"📋 آخرین برنامه هفتگی شما:\n\n{result[0]}")
        else:
            await update.message.reply_text("برنامه‌ای ثبت نشده است.\nبرای ثبت: /weeklyplan [متن برنامه]")

async def daily_check_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
📊 چک‌لیست شروع بازار روزانه

1. اخبار اقتصادی امروز را بررسی کنید.
2. سشن معاملاتی فعال را مشخص کنید.
3. جفت‌ارزهای اصلی را بررسی کنید.
4. سطوح کلیدی حمایت و مقاومت را مشخص کنید.
5. حجم بازار را بررسی کنید.

آیا همه موارد بررسی شد؟
"""
    await update.message.reply_text(message)

async def pre_trade_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """
⚠️ چک‌لیست قبل از ورود به معامله

1. آیا در جهت روند اصلی وارد می‌شوید؟
2. آیا نسبت ریسک به ریوارد حداقل 1:2 است؟
3. آیا حجم معامله مناسب است (1 تا 2 درصد حساب)؟
4. آیا اخبار مهمی در راه نیست؟
5. آیا ستاپ معاملاتی شما کامل است؟
6. آیا احساسات شما تحت کنترل است؟

فقط اگر همه موارد تأیید شد، وارد معامله شوید.
"""
    await update.message.reply_text(message)

async def add_error_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if context.args:
        error = ' '.join(context.args)
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO errors (user_id, error_text, date) VALUES (?, ?, ?)", (user_id, error, date))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"❌ خطا ثبت شد:\n{error}")
    else:
        await update.message.reply_text("لطفاً خطا را توضیح دهید:\n/adderror [توضیح خطا]")

async def add_achievement_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if context.args:
        achievement = ' '.join(context.args)
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO achievements (user_id, achievement_text, date) VALUES (?, ?, ?)", (user_id, achievement, date))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"🏆 دستاورد ثبت شد:\n{achievement}")
    else:
        await update.message.reply_text("لطفاً دستاورد خود را توضیح دهید:\n/addachievement [توضیح دستاورد]")

async def show_errors_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT error_text, date FROM errors WHERE user_id=? ORDER BY rowid DESC LIMIT 10", (user_id,))
    results = cursor.fetchall()
    conn.close()

    if results:
        errors_list = "\n".join([f"{r[1]}: {r[0]}" for r in reversed(results)])
        await update.message.reply_text(f"❌ خطاهای ثبت شده:\n\n{errors_list}")
    else:
        await update.message.reply_text("هیچ خطایی ثبت نشده است.")

async def show_achievements_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT achievement_text, date FROM achievements WHERE user_id=? ORDER BY rowid DESC LIMIT 10", (user_id,))
    results = cursor.fetchall()
    conn.close()

    if results:
        achievements_list = "\n".join([f"{r[1]}: {r[0]}" for r in reversed(results)])
        await update.message.reply_text(f"🏆 دستاوردهای ثبت شده:\n\n{achievements_list}")
    else:
        await update.message.reply_text("هیچ دستاوردی ثبت نشده است.")

# --- دستورات فایل‌های مارک‌داون ---
async def checklist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_md_file(update, context, 'checklist.md')

async def strategy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_md_file(update, context, 'strategy.md')

async def weekly_review_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_md_file(update, context, 'weekly_review.md')

# --- تنظیمات Flask و اجرا ---
app = Flask(__name__)

@app.route('/')
def home():
    return "ربات هرمس در حال اجرا است..."

def run_bot():
    async def main():
        application = Application.builder().token(TOKEN).build()

        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("weeklyplan", weekly_plan_command))
        application.add_handler(CommandHandler("dailycheck", daily_check_command))
        application.add_handler(CommandHandler("pretrade", pre_trade_command))
        application.add_handler(CommandHandler("adderror", add_error_command))
        application.add_handler(CommandHandler("addachievement", add_achievement_command))
        application.add_handler(CommandHandler("showerrors", show_errors_command))
        application.add_handler(CommandHandler("showachievements", show_achievements_command))
        application.add_handler(CommandHandler("checklist", checklist_command))
        application.add_handler(CommandHandler("strategy", strategy_command))
        application.add_handler(CommandHandler("weeklyreview", weekly_review_command))

        print("✅ ربات هرمس با تمام قابلیت‌ها اجرا شد...")
        await application.run_polling(allowed_updates=Update.ALL_TYPES)

    asyncio.run(main())

if __name__ == '__main__':
    init_db()
    os.makedirs('content', exist_ok=True)

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    app.run(host='0.0.0.0', port=8080)
