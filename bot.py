import os
import sys

# نصب خودکار کتابخانه‌ها قبل از import
os.system(f"{sys.executable} -m pip install requests")
os.system(f"{sys.executable} -m pip install beautifulsoup4")
os.system(f"{sys.executable} -m pip install python-telegram-bot==22.8")
os.system(f"{sys.executable} -m pip install qrcode[pil]")
os.system(f"{sys.executable} -m pip install jdatetime")

import json
import random
import string
import requests
from pathlib import Path
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

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

# ============ استخراج قیمت‌ها ============

def get_price_tgju(item_name):
    try:
        url = "https://www.tgju.org"
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 2:
                name = cells[0].get_text(strip=True)
                if item_name in name:
                    return cells[1].get_text(strip=True)
        return None
    except:
        return None

def get_price_arzdigital(item_name):
    try:
        url = "https://arzdigital.com/currencies/"
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 2:
                name = cells[0].get_text(strip=True)
                if item_name in name:
                    return cells[1].get_text(strip=True)
        return None
    except:
        return None

def get_price_chandshode(item_name):
    try:
        url = "https://chandshode.com"
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup.find_all(["h3", "h4", "h5", "span", "div"]):
            text = tag.get_text(strip=True)
            if item_name in text:
                parent = tag.find_parent()
                if parent:
                    price_text = parent.get_text(strip=True)
                    import re
                    numbers = re.findall(r'[\d,]+', price_text)
                    if numbers:
                        return numbers[0] + " تومان"
        return None
    except:
        return None

def get_all_prices(item_name):
    return {
        "tgju.org": get_price_tgju(item_name),
        "arzdigital.com": get_price_arzdigital(item_name),
        "chandshode.com": get_price_chandshode(item_name),
    }

# ============ بررسی عضویت ============
async def is_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=update.effective_user.id)
        return member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except:
        return False

# ============ دکمه‌ها ============
def join_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 عضویت در کانال چی شده؟", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ عضو شدم", callback_data="check_join")]
    ])

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 قیمت‌ها", callback_data="menu_prices"),
         InlineKeyboardButton("📊 اطلاعات", callback_data="menu_info")],
        [InlineKeyboardButton("🛠 ابزار", callback_data="menu_tools"),
         InlineKeyboardButton("📩 پشتیبانی", callback_data="menu_support")],
        [InlineKeyboardButton("ℹ️ درباره ربات", callback_data="menu_about"),
         InlineKeyboardButton("📞 تماس با ما", callback_data="menu_contact")],
    ])

def prices_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💵 دلار", callback_data="price_dollar")],
        [InlineKeyboardButton("🪙 تتر", callback_data="price_tether"),
         InlineKeyboardButton("🥇 طلا", callback_data="price_gold")],
        [InlineKeyboardButton("💶 یورو", callback_data="price_euro"),
         InlineKeyboardButton("🪙 سکه", callback_data="price_coin")],
        [InlineKeyboardButton("💷 پوند", callback_data="price_pound"),
         InlineKeyboardButton("📊 بقیه ارزها", callback_data="price_others")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_back")],
    ])

def welcome_text(first_name):
    return (
        f"سلام {first_name} عزیز 👋\n\n"
        "به ربات **42 ++** خوش اومدی 🌹\n\n"
        "اینجا هر چی بخوای هست:\n"
        "💰 قیمت لحظه‌ای ارز و طلا\n"
        "📊 اطلاعات\n"
        "🛠 ابزار کاربردی\n"
        "📩 پشتیبانی\n\n"
        "از منوی زیر انتخاب کن 👇"
    )

# ============ دستور /start ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id)

    if not await is_member(update, context):
        await update.message.reply_text(
            f"سلام {user.first_name} عزیز 👋\n\nبه ربات **42 ++** خوش اومدی.\n\n📢 برای استفاده از ربات، اول توی کانالمون عضو شو:",
            reply_markup=join_keyboard(),
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(welcome_text(user.first_name), reply_markup=main_menu_keyboard(), parse_mode="Markdown")

# ============ دستور /join ============
async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("برای عضویت روی دکمه زیر بزن:", reply_markup=join_keyboard())

# ============ دستور /price ============
async def price_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_member(update, context):
        await update.message.reply_text("⚠️ اول توی کانال عضو شو:", reply_markup=join_keyboard())
        return
    await update.message.reply_text("درود بر شما 🌹\nدنبال قیمت چه چیزی هستی؟", reply_markup=prices_keyboard())

# ============ نمایش قیمت ============
async def show_price(query, context, item_name, title):
    await query.edit_message_text("⏳ در حال جستجو در سایت‌ها...")
    results = get_all_prices(item_name)
    text = f"**{title}**\n\n"
    for site, price in results.items():
        if price:
            text += f"✅ {site}: {price}\n"
        else:
            text += f"❌ {site}: پیدا نشد\n"
    now = datetime.now().strftime("%H:%M")
    text += f"\n🕐 آخرین بروزرسانی: {now}"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"refresh_{item_name}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_prices")]
    ])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)

# ============ هندلر دکمه‌ها ============
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_join":
        if await is_member(update, context):
            await query.edit_message_text(welcome_text(update.effective_user.first_name), reply_markup=main_menu_keyboard(), parse_mode="Markdown")
        else:
            await query.edit_message_text("❌ هنوز عضو نشدی!\n\nاول توی کانال عضو شو، بعد دوباره روی «عضو شدم» بزن.", reply_markup=join_keyboard())

    elif query.data == "menu_prices":
        await query.edit_message_text("درود بر شما 🌹\nدنبال قیمت چه چیزی هستی؟", reply_markup=prices_keyboard())

    elif query.data == "price_dollar":
        await show_price(query, context, "دلار", "💵 قیمت دلار")

    elif query.data == "price_tether":
        await show_price(query, context, "تتر", "🪙 قیمت تتر")

    elif query.data == "price_gold":
        await show_price(query, context, "طلای 18", "🥇 قیمت طلا")

    elif query.data == "price_euro":
        await show_price(query, context, "یورو", "💶 قیمت یورو")

    elif query.data == "price_coin":
        await show_price(query, context, "سکه امامی", "🪙 قیمت سکه")

    elif query.data == "price_pound":
        await show_price(query, context, "پوند", "💷 قیمت پوند")

    elif query.data == "price_others":
        await query.edit_message_text(f"📊 **بقیه ارزها**\n\nبرای دیدن لیست کامل، به کانال ما سر بزن:\n{CHANNEL_LINK}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_prices")]]))

    elif query.data == "menu_info":
        await query.edit_message_text("📊 **اطلاعات**\n\n🔹 /time — ساعت و تاریخ\n🔹 /id — آیدی عددی شما", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_back")]]))

    elif query.data == "menu_tools":
        await query.edit_message_text("🛠 **ابزار کاربردی**\n\n🔹 /password — ساخت رمز قوی\n🔹 /calc — ماشین حساب\n🔹 /qr — ساخت QR کد\n🔹 /remind — یادآور", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_back")]]))

    elif query.data == "menu_support":
        await query.edit_message_text("📩 **پشتیبانی**\n\nبا دستور /support پیامت رو برای تیم پشتیبانی بفرست.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_back")]]))

    elif query.data == "menu_about":
        await query.edit_message_text(f"ℹ️ **درباره ربات 42 ++**\n\nربات 42 ++ یک ربات همه‌کاره تلگرامیه.\n\n📢 کانال: {CHANNEL_USERNAME}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_back")]]))

    elif query.data == "menu_contact":
        await query.edit_message_text(f"📞 **تماس با ما**\n\n📢 کانال: {CHANNEL_USERNAME}\n\nبرای پشتیبانی، /support رو بزن.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="menu_back")]]))

    elif query.data == "menu_back":
        await query.edit_message_text(welcome_text(update.effective_user.first_name), reply_markup=main_menu_keyboard(), parse_mode="Markdown")

    elif query.data.startswith("refresh_"):
        item = query.data.replace("refresh_", "")
        await show_price(query, context, item, f"🔄 بروزرسانی قیمت {item}")

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
    await update.message.reply_text(f"🔐 **رمز عبور قوی**\n\n`{pwd}`\n\n⚠️ این رمز رو جای امنی ذخیره کن.", parse_mode="Markdown")

# ============ دستور /calc ============
async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("مثال:\n`/calc 2+3`\n`/calc 10*5`\n`/calc 100/4`", parse_mode="Markdown")
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
        await update.message.reply_text("مثال:\n`/qr سلام`\n`/qr https://t.me/chishoeh`", parse_mode="Markdown")
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
        await update.message.reply_text("مثال:\n`/remind 10 سلام کردن`", parse_mode="Markdown")
        return
    try:
        minutes = int(context.args[0])
        text = " ".join(context.args[1:])
        chat_id = update.effective_chat.id
        await update.message.reply_text(f"⏰ باشه، {minutes} دقیقه دیگه یادت می‌ندازم.")
        context.job_queue.run_once(send_reminder, when=timedelta(minutes=minutes), data={"chat_id": chat_id, "text": text}, name=f"remind_{chat_id}")
    except:
        await update.message.reply_text("❌ خطا. مثال: `/remind 10 سلام`", parse_mode="Markdown")

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(chat_id=job.data["chat_id"], text=f"⏰ **یادآوری:**\n{job.data['text']}", parse_mode="Markdown")

# ============ دستور /support ============
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📩 **پشتیبانی**\n\nپیامت رو بنویس، برای تیم پشتیبانی می‌فرستم.\n\n⚠️ پیامت رو با متن معمولی بنویس (بدون دستور).", parse_mode="Markdown")
    context.user_data["waiting_for_support"] = True

# ============ پردازش پیام پشتیبانی ============
async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_for_support"):
        return
    if not await is_member(update, context):
        await update.message.reply_text("⚠️ اول توی کانال عضو شو:", reply_markup=join_keyboard())
        return
    user = update.effective_user
    text = update.message.text
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"📩 **پیام پشتیبانی جدید**\n\n👤 از: {user.first_name}\n🆔 آیدی: `{user.id}`\n📛 یوزرنیم: @{user.username if user.username else 'نداری'}\n\n💬 پیام:\n{text}\n\n📌 برای پاسخ:\n`/reply {user.id} متن جواب`",
                parse_mode="Markdown"
            )
        except:
            pass
    await update.message.reply_text("✅ پیامت برای تیم پشتیبانی ارسال شد.\nبه‌زودی جواب می‌گیری.")
    context.user_data["waiting_for_support"] = False

# ============ دستور /reply (ادمین) ============
async def reply_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if len(context.args) < 2:
        await update.message.reply_text("مثال:\n`/reply 123456789 سلام، مشکل حل شد.`", parse_mode="Markdown")
        return
    try:
        user_id = int(context.args[0])
        text = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=user_id, text=f"📩 **پاسخ پشتیبانی:**\n\n{text}", parse_mode="Markdown")
        await update.message.reply_text("✅ پاسخ ارسال شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

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
        await update.message.reply_text("متن پیام رو بعد از دستور بنویس:\n\nمثال:\n/broadcast سلام به همه دوستان")
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
    await msg.edit_text(f"✅ ارسال تمام شد.\n\n👥 کل کاربران: {len(users)}\n✅ موفق: {sent}\n🚫 بلاک کردن: {blocked}\n❌ ناموفق: {failed}")

# ============ هندلر پیام‌های عادی ============
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id)
    if context.user_data.get("waiting_for_support"):
        if update.message.text:
            await handle_support(update, context)
        return
    if not await is_member(update, context):
        await update.message.reply_text("⚠️ برای استفاده از ربات، اول توی کانال عضو شو:", reply_markup=join_keyboard())
        return
    await update.message.reply_text("متوجه نشدم 🤔\nبرای دیدن دستورات، /help رو بزن.")

# ============ دستور /help ============
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 **راهنمای ربات 42 ++**\n\n"
        "🔹 /start — شروع و منوی اصلی\n"
        "🔹 /join — عضویت در کانال\n"
        "🔹 /price — قیمت‌های لحظه‌ای\n"
        "🔹 /time — ساعت و تاریخ\n"
        "🔹 /id — آیدی عددی شما\n"
        "🔹 /password — ساخت رمز قوی\n"
        "🔹 /calc — ماشین حساب\n"
        "🔹 /qr — ساخت QR کد\n"
        "🔹 /remind — یادآور\n"
        "🔹 /support — پشتیبانی\n"
        "🔹 /about — درباره ربات\n"
        "🔹 /contact — تماس با ما\n"
    )
    if update.effective_user.id in ADMIN_IDS:
        text += "\n🔐 **دستورات ادمین:**\n🔸 /stats — آمار کاربران\n🔸 /broadcast متن — پیام همگانی\n🔸 /reply آیدی متن — پاسخ به کاربر\n"
    await update.message.reply_text(text, parse_mode="Markdown")

# ============ دستور /about ============
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"ℹ️ **درباره ربات 42 ++**\n\nربات 42 ++ یک ربات همه‌کاره تلگرامیه.\n\n📢 کانال ما: {CHANNEL_USERNAME}", parse_mode="Markdown")

# ============ دستور /contact ============
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📞 **راه‌های ارتباطی**\n\n📢 کانال: {CHANNEL_USERNAME}\n\nبرای ارتباط با پشتیبانی، از دستور /support استفاده کن.", parse_mode="Markdown")

# ============ اجرا ============
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("price", price_cmd))
    app.add_handler(CommandHandler("time", time_cmd))
    app.add_handler(CommandHandler("id", id_cmd))
    app.add_handler(CommandHandler("password", password_cmd))
    app.add_handler(CommandHandler("calc", calc))
    app.add_handler(CommandHandler("qr", qr_cmd))
    app.add_handler(CommandHandler("remind", remind))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("reply", reply_cmd))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    print("ربات روشن شد")
    app.run_polling()

if __name__ == '__main__':
    main()
