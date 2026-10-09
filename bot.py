import os
import subprocess
import sys

subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot==22.8"])

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("عضویت در کانال چی شده؟", url="https://t.me/chishoeh")]]
    await update.message.reply_text("برای عضویت روی دکمه زیر بزن:", reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("join", join))
    print("ربات روشن شد")
    app.run_polling()

if __name__ == '__main__':
    main()
