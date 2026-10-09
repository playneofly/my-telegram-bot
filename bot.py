import os
import subprocess
import sys
import json
from pathlib import Path

subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot==22.8"])

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters

# ============ تنظیمات ============
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_USERNAME = "@chishoeh"
CHANNEL_LINK = "https://t.me/chishoeh"

# ✅ آیدی ادمین
ADMIN_IDS = [6218785645]

USERS_FILE = Path("users.json")

# ============ توابع کمکی ============
def load_users():
    if USERS_FILE.exists():
        try:
            return set(json.loads(USERS_FILE.read_text()))
        except:
            return set()
    return set()

def save_users(users):
    USERS_FILE.write_text(json.dumps(list(users)))

def add_user(user_id):
    users = load_users()
    if user_id not in users:
        users.add(user_id)
        save_users(users)

# ============ بررسی عضویت ============
async def is_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=update.effective_user.id
        )
        return member.status in [
            ChatMember.MEMBER,
            ChatMember.ADMINISTRATOR,
            ChatMember.OWNER
        ]
    except:
        return False

# ============ دکمه عضویت ============
def join_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 عضویت در کانال چی شده؟", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ عضو شدم", callback_data="check_join")]
    ])

# ============ دستور /start ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id)

    await update.message.reply_text(
        f"سلام {user.first_name} عزیز 👋\n\n"
        "به ربات «چی شده؟» خوش اومدی.\n\n"
        "📢 برای استفاده از ربات، اول توی کانالمون عضو شو:",
        reply_markup=join_keyboard()
    )

# ============ دستور /join ============
async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "برای عضویت روی دکمه زیر بزن:",
        reply_markup=join_keyboard()
    )

# ============ دستور /help ============
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 راهنمای ربات:\n\n"
        "/start - شروع\n"
        "/join - عضویت در کانال\n"
        "/help - همین راهنما\n"
    )
    if update.effective_user.id in ADMIN_IDS:
        text += (
            "\n🔐 دستورات ادمین:\n"
            "/stats - آمار کاربران\n"
            "/broadcast متن - ارسال پیام همگانی\n"
        )
    await update.message.reply_text(text)

# ============ دستور /stats (ادمین) ============
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    users = load_users()
    await update.message.reply_text(f"👥 تعداد کاربران ربات: {len(users)}")

# ============ دستور /broadcast (ادمین) ============
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if not context.args:
        await update.message.reply_text(
            "متن پیام رو بعد از دستور بنویس:\n\n"
            "مثال:\n/broadcast سلام به همه دوستان"
        )
        return

    text = " ".join(context.args)
    users = load_users()
    sent = 0
    failed = 0

    msg = await update.message.reply_text("⏳ در حال ارسال...")

    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=text)
            sent += 1
        except:
            failed += 1

    await msg.edit_text(
        f"✅ ارسال تمام شد.\n\n"
        f"موفق: {sent}\n"
        f"ناموفق: {failed}"
    )

# ============ هندلر دکمه "عضو شدم" ============
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_join":
        if await is_member(update, context):
            await query.edit_message_text(
                "✅ عضویتت تأیید شد!\n\n"
                "حالا می‌تونی از ربات استفاده کنی. 🎉"
            )
        else:
            await query.edit_message_text(
                "❌ هنوز عضو نشدی!\n\n"
                "اول توی کانال عضو شو، بعد دوباره روی «عضو شدم» بزن.",
                reply_markup=join_keyboard()
            )

# ============ هندلر پیام‌های عادی ============
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id)

    if not await is_member(update, context):
        await update.message.reply_text(
            "⚠️ برای استفاده از ربات، اول توی کانال عضو شو:",
            reply_markup=join_keyboard()
        )
        return

    await update.message.reply_text("پیامت دریافت شد ✅")

# ============ اجرا ============
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("ربات روشن شد")
    app.run_polling()

if __name__ == '__main__':
    main()
