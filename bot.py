from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("عضویت در کانال چی شده؟", url="https://t.me/chishoeh")]]
    await update.message.reply_text("برای عضویت روی دکمه زیر بزن:", reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    app = Application.builder().token("8616247409:AAFWLykWs-pIu8h2GSKYzP0n7eoZ2GES_i0").build()
    app.add_handler(CommandHandler("join", join))
    print("ربات روشن شد")
    app.run_polling()

if __name__ == '__main__':
    main()