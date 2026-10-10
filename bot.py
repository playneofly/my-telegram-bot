import os
import subprocess
import sys
import json
import random
import string
from pathlib import Path
from datetime import datetime, timedelta

subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot==22.8"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "qrcode[pil]"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "jdatetime"])

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters
import qrcode
import jdatetime

# ============ تنظیمات ============
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_USERNAME = "@chishoeh"
CHANNEL_LINK = "https://t.me/chishoeh"
ADMIN_IDS = [6218785645]
ADMIN_USERNAME = "@alrznsb"

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

# ============ دکمه‌های منوی اصلی ============
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 اطلاعات", callback_data="menu_info"),
         InlineKeyboardButton("🛠 ابزار", callback_data="menu_tools")],
        [InlineKeyboardButton("📥 دانلودر", callback_data="menu_download"),
         InlineKeyboardButton("📖 راهنما", callback_data="menu_help")],
        [InlineKeyboardButton("ℹ️ درباره ربات", callback_data="menu_about"),
         InlineKeyboardButton("📞 تماس با ما", callback_data="menu_contact")],
    ])

# ============ متن خوش‌آمد ============
def welcome_text(first_name):
    return (
        f"سلام {first_name} عزیز 👋\n\n"
        "به ربات **42 ++** خوش اومدی 🌹\n\n"
        "اینجا هر چی بخوای هست:\n"
        "📊 اطلاعات\n"
        "🛠 ابزار کاربردی\n"
        "📥 دانلود از شبکه‌های اجتماعی\n\n"
        "از منوی زیر انتخاب کن 👇"
    )

# ============ دستور /start ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id)

    if not await is_member(update, context):
        await update.message.reply_text(
            f"سلام {user.first_name} عزیز 👋\n\n"
            "به ربات **42 ++** خوش اومدی.\n\n"
            "📢 برای استفاده از ربات، اول توی کانالمون عضو شو:",
            reply_markup=join_keyboard(),
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        welcome_text(user.first_name),
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
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
        "📖 **راهنمای ربات 42 ++**\n\n"
        "🔹 /start — شروع و منوی اصلی\n"
        "🔹 /join — عضویت در کانال\n"
        "🔹 /time — ساعت و تاریخ\n"
        "🔹 /id — آیدی عددی شما\n"
        "🔹 /password — ساخت رمز قوی\n"
        "🔹 /calc — ماشین حساب (مثال: /calc 2+3)\n"
        "🔹 /qr — ساخت QR کد (مثال: /qr سلام)\n"
        "🔹 /remind — یادآور (مثال: /remind 10 متن)\n"
        "🔹 /about — درباره ربات\n"
        "🔹 /contact — تماس با ما\n"
    )
    if update.effective_user.id in ADMIN_IDS:
        text += (
            "\n🔐 **دستورات ادمین:**\n"
            "🔸 /stats — آمار کاربران\n"
            "🔸 /broadcast متن — پیام همگانی\n"
        )
    await update.message.reply_text(text, parse_mode="Markdown")

# ============ دستور /about ============
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ **درباره ربات 42 ++**\n\n"
        "ربات 42 ++ یک ربات همه‌کاره تلگرامیه که "
        "ابزارهای کاربردی، اطلاعات و دانلودر رو در اختیارت می‌ذاره.\n\n"
        f"📢 کانال ما: {CHANNEL_USERNAME}\n"
        f"👤 ادمین: {ADMIN_USERNAME}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ============ دستور /contact ============
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📞 **راه‌های ارتباطی**\n\n"
        f"👤 ادمین: {ADMIN_USERNAME}\n"
        f"📢 کانال: {CHANNEL_USERNAME}\n\n"
        "برای ارتباط با ادمین، به آیدی بالا پیام بده."
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ============ دستور /time ============
async def time_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    jalali = jdatetime.datetime.fromgregorian(datetime=now)

    text = (
        "🕐 **ساعت و تاریخ**\n\n"
        f"📅 تاریخ شمسی: {jalali.strftime('%Y/%m/%d')}\n"
        f"📅 تاریخ میلادی: {now.strftime('%Y/%m/%d')}\n"
        f"⏰ ساعت: {now.strftime('%H:%M:%S')}\n"
        f"📆 روز هفته: {jalali.strftime('%A')}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ============ دستور /id ============
async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        "🆔 **اطلاعات شما**\n\n"
        f"👤 نام: {user.first_name}\n"
        f"🔢 آیدی عددی: `{user.id}`\n"
        f"📛 یوزرنیم: @{user.username if user.username else 'نداری'}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ============ دستور /password ============
async def password_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    length = 16
    if context.args:
        try:
            length = int(context.args[0])
            if length < 6 or length > 64:
                length = 16
        except:
            length = 16

    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    pwd = "".join(random.choice(chars) for _ in range(length))

    text = (
        "🔐 **رمز عبور قوی**\n\n"
        f"`{pwd}`\n\n"
        "⚠️ این رمز رو جای امنی ذخیره کن."
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ============ دستور /calc ============
async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "مثال:\n`/calc 2+3`\n`/calc 10*5`\n`/calc 100/4`",
            parse_mode="Markdown"
        )
        return

    expr = " ".join(context.args)
    try:
        result = eval(expr, {"__builtins__": {}}, {})
        await update.message.reply_text(f"🧮 `{expr}` = `{result}`", parse_mode="Markdown")
    except:
        await update.message.reply_text("❌ عبارت نامعتبره. مثال: `/calc 2+3`", parse_mode="Markdown")

# ============ دستور /qr ============
async def qr_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "مثال:\n`/qr سلام`\n`/qr https://t.me/chishoeh`",
            parse_mode="Markdown"
        )
        return

    text = " ".join(context.args)
    try:
        img = qrcode.make(text)
        path = f"qr_{update.effective_user.id}.png"
        img.save(path)

        with open(path, "rb") as f:
            await update.message.reply_photo(photo=f, caption=f"✅ QR کد ساخته شد:\n`{text}`", parse_mode="Markdown")

        os.remove(path)
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

# ============ دستور /remind ============
async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text(
            "مثال:\n`/remind 10 سلام کردن`\n(۱۰ دقیقه دیگه یادآوری کن)",
            parse_mode="Markdown"
        )
        return

    try:
        minutes = int(context.args[0])
        text = " ".join(context.args[1:])
        chat_id = update.effective_chat.id

        await update.message.reply_text(f"⏰ باشه، {minutes} دقیقه دیگه یادت می‌ندازم.")

        context.job_queue.run_once(
            send_reminder,
            when=timedelta(minutes=minutes),
            data={"chat_id": chat_id, "text": text},
            name=f"remind_{chat_id}"
        )
    except:
        await update.message.reply_text("❌ خطا. مثال: `/remind 10 سلام`", parse_mode="Markdown")

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(
        chat_id=job.data["chat_id"],
        text=f"⏰ **یادآوری:**\n{job.data['text']}",
        parse_mode="Markdown"
    )

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

    if len(users) == 0:
        await update.message.reply_text("❌ لیست کاربران خالیه!")
        return

    sent = 0
    failed = 0
    blocked = 0

    msg = await update.message.reply_text(f"⏳ در حال ارسال به {len(users)} کاربر...")

    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=text)
            sent += 1
        except Exception as e:
            if "blocked" in str(e).lower() or "chat not found" in str(e).lower():
                blocked += 1
            else:
                failed += 1

    await msg.edit_text(
        f"✅ ارسال تمام شد.\n\n"
        f"👥 کل کاربران: {len(users)}\n"
        f"✅ موفق: {sent}\n"
        f"🚫 بلاک کردن: {blocked}\n"
        f"❌ ناموفق: {failed}"
    )

# ============ هندلر دکمه‌ها ============
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_join":
        if await is_member(update, context):
            await query.edit_message_text(
                welcome_text(update.effective_user.first_name),
                reply_markup=main_menu_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                "❌ هنوز عضو نشدی!\n\n"
                "اول توی کانال عضو شو، بعد دوباره روی «عضو شدم» بزن.",
                reply_markup=join_keyboard()
            )

    elif query.data == "menu_info":
        await query.edit_message_text(
            "📊 **اطلاعات**\n\n"
            "🔹 /time — ساعت و تاریخ\n"
            "🔹 /id — آیدی عددی شما\n\n"
            "به‌زودی: نرخ ارز، آب و هوا، اخبار",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_back")]
            ])
        )

    elif query.data == "menu_tools":
        await query.edit_message_text(
            "🛠 **ابزار کاربردی**\n\n"
            "🔹 /password — ساخت رمز قوی\n"
            "🔹 /calc — ماشین حساب\n"
            "🔹 /qr — ساخت QR کد\n"
            "🔹 /remind — یادآور",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_back")]
            ])
        )

    elif query.data == "menu_download":
        await query.edit_message_text(
            "📥 **دانلودر**\n\n"
            "🔹 اینستاگرام\n"
            "🔹 یوتیوب\n"
            "🔹 تیک‌تاک\n\n"
            "⚠️ به‌زودی اضافه میشه!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_back")]
            ])
        )

    elif query.data == "menu_help":
        await query.edit_message_text(
            "📖 برای دیدن راهنما، دستور /help رو بزن.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_back")]
            ])
        )

    elif query.data == "menu_about":
        await query.edit_message_text(
            "ℹ️ **درباره ربات 42 ++**\n\n"
            "ربات 42 ++ یک ربات همه‌کاره تلگرامیه.\n\n"
            f"📢 کانال: {CHANNEL_USERNAME}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_back")]
            ])
        )

    elif query.data == "menu_contact":
        await query.edit_message_text(
            f"📞 **تماس با ما**\n\n"
            f"👤 ادمین: {ADMIN_USERNAME}\n"
            f"📢 کانال: {CHANNEL_USERNAME}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_back")]
            ])
        )

    elif query.data == "menu_back":
        await query.edit_message_text(
            welcome_text(update.effective_user.first_name),
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown"
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

    await update.message.reply_text(
        "متوجه نشدم 🤔\n"
        "برای دیدن دستورات، /help رو بزن."
    )

# ============ اجرا ============
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("time", time_cmd))
    app.add_handler(CommandHandler("id", id_cmd))
    app.add_handler(CommandHandler("password", password_cmd))
    app.add_handler(CommandHandler("calc", calc))
    app.add_handler(CommandHandler("qr", qr_cmd))
    app.add_handler(CommandHandler("remind", remind))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("ربات روشن شد")
    app.run_polling()

if __name__ == '__main__':
    main()
