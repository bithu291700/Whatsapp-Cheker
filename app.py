import os
import requests
from pymongo import MongoClient
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    MessageHandler, ContextTypes, ConversationHandler, filters
)

# ----------------- ENVIRONMENT VARIABLES -----------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
SMSBOWER_API_KEY = os.getenv("SMSBOWER_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
OTP_GROUP_ID = os.getenv("OTP_GROUP_ID")
MONGO_URI = os.getenv("MONGO_URI")

ADMIN_BKASH = "01858582881"
SUB_PRICE_BDT = 30

# ----------------- DATABASE SETUP -----------------
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["sms_bot_db"]

users_col = db["users"]
services_col = db["services"]
orders_col = db["active_orders"]
subs_col = db["subscriptions"]

SUB_TRX, SUB_SS = range(2)

# ----------------- KEYBOARDS -----------------

def get_main_keyboard(is_subscribed=False):
    if not is_subscribed:
        keyboard = [[KeyboardButton("💳 সাবস্ক্রিপশন কিনুন (৳৩০)")]]
    else:
        keyboard = [
            [KeyboardButton("📱 Buy Number"), KeyboardButton("💳 Deposit (Binance)")],
            [KeyboardButton("👤 Profile & Balance"), KeyboardButton("📋 My History")],
            [KeyboardButton("❓ Help & Support")]
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard():
    keyboard = [
        [KeyboardButton("➕ Add Service"), KeyboardButton("💰 Set Custom Balance")],
        [KeyboardButton("👥 View Subscribed History"), KeyboardButton("📢 Broadcast")],
        [KeyboardButton("🚫 Ban User"), KeyboardButton("✅ Unban User")],
        [KeyboardButton("🔙 Main Menu")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ----------------- START HANDLER -----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    user = users_col.find_one({"user_id": user_id})
    if not user:
        user = {
            "user_id": user_id,
            "name": user_name,
            "balance": 0.0,
            "is_subscribed": False,
            "is_banned": False,
            "history": []
        }
        users_col.insert_one(user)

    if user.get("is_banned", False):
        await update.message.reply_text("❌ আপনাকে বোটে ব্যান করা হয়েছে।")
        return

    if user_id == ADMIN_ID:
        await update.message.reply_text("👑 **অ্যাডমিন প্যানেলে স্বাগতম!**", reply_markup=get_admin_keyboard(), parse_mode="Markdown")
        return

    if not user.get("is_subscribed", False):
        msg = (
            f"👋 **হ্যালো {user_name}!**\n\n"
            f"⚠️ **বোটের সেবা ব্যবহার করতে আপনাকে সাবস্ক্রিপশন নিতে হবে।**\n\n"
            f"📌 **সাবস্ক্রিপশন ফি:** ৳{SUB_PRICE_BDT} BDT\n"
            f"পেমেন্ট করতে নিচে **'💳 সাবস্ক্রিপশন কিনুন (৳৩০)'** বাটনে ক্লিক করুন।"
        )
        await update.message.reply_text(msg, reply_markup=get_main_keyboard(is_subscribed=False), parse_mode="Markdown")
    else:
        balance = user.get("balance", 0.0)
        msg = f"👋 **স্বাগতম!**\n\n💳 আপনার বর্তমান ব্যালেন্স: **${balance:.2f}**"
        await update.message.reply_text(msg, reply_markup=get_main_keyboard(is_subscribed=True), parse_mode="Markdown")

# ----------------- SUBSCRIPTION FLOW -----------------

async def start_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = users_col.find_one({"user_id": user_id})
    
    if user and user.get("is_subscribed", False):
        await update.message.reply_text("✅ আপনার সাবস্ক্রিপশন ইতোমধ্যে চালু রয়েছে!")
        return ConversationHandler.END

    text = (
        f"📱 **বিকাশ সেন্ড মানি করুন:**\n\n"
        f"নম্বর: `{ADMIN_BKASH}` (Personal)\n"
        f"পরিমাণ: **৳{SUB_PRICE_BDT} BDT**\n\n"
        f"টাকা পাঠানোর পর নিচে আপনার **TrxID** লিখে পাঠান:"
    )
    await update.message.reply_text(text, parse_mode="Markdown")
    return SUB_TRX

async def get_trx_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["trx_id"] = update.message.text.strip()
    await update.message.reply_text("📸 এবার বিকাশ পেমেন্টের **স্ক্রিনশট (Screenshot)** পাঠান:")
    return SUB_SS

async def get_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    trx_id = context.user_data.get("trx_id")
    photo_file_id = update.message.photo[-1].file_id

    subs_col.insert_one({
        "user_id": user_id,
        "trx_id": trx_id,
        "photo_id": photo_file_id,
        "status": "pending"
    })

    await update.message.reply_text("⏳ আপনার সাবস্ক্রিপশন রিকোয়েস্ট অ্যাডমিনের কাছে পাঠানো হয়েছে।")

    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"sub_app_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"sub_rej_{user_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    admin_msg = (
        f"🔔 **নতুন সাবস্ক্রিপশন রিকোয়েস্ট!**\n\n"
        f"👤 ইউজার: {user_name} (`{user_id}`)\n"
        f"🆔 TrxID: `{trx_id}`\n"
        f"💰 পরিমাণ: ৳{SUB_PRICE_BDT} BDT"
    )
    await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_file_id, caption=admin_msg, reply_markup=reply_markup, parse_mode="Markdown")
    return ConversationHandler.END

async def handle_sub_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    target_user_id = int(data.split("_")[2])

    if "sub_app_" in data:
        users_col.update_one({"user_id": target_user_id}, {"$set": {"is_subscribed": True}})
        subs_col.update_one({"user_id": target_user_id}, {"$set": {"status": "approved"}})

        await query.edit_message_caption(caption=f"{query.message.caption}\n\n✅ **Approved!**")
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text="🎉 **আপনার সাবস্ক্রিপশন সফলভাবে অনুমোদিত হয়েছে!**",
                reply_markup=get_main_keyboard(is_subscribed=True)
            )
        except Exception:
            pass

    elif "sub_rej_" in data:
        subs_col.update_one({"user_id": target_user_id}, {"$set": {"status": "rejected"}})
        await query.edit_message_caption(caption=f"{query.message.caption}\n\n❌ **Rejected!**")
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text="❌ আপনার সাবস্ক্রিপশন রিকোয়েস্টটি বাতিল করা হয়েছে।"
            )
        except Exception:
            pass

# ----------------- MAIN USER/ADMIN ROUTER -----------------

async def handle_user_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    user = users_col.find_one({"user_id": user_id})

    if not user or user.get("is_banned", False):
        return

    if user_id != ADMIN_ID and not user.get("is_subscribed", False):
        await update.message.reply_text("⚠️ পূর্বে সাবস্ক্রিপশন সম্পন্ন করুন!", reply_markup=get_main_keyboard(is_subscribed=False))
        return

    if text == "📱 Buy Number":
        active_order = orders_col.find_one({"user_id": user_id})
        if active_order:
            keyboard = [
                [InlineKeyboardButton("🔄 Check OTP", callback_data=f"chk_otp_{active_order['activation_id']}")],
                [InlineKeyboardButton("❌ Cancel Order", callback_data=f"cancel_{active_order['activation_id']}")]
            ]
            await update.message.reply_text(
                f"⚠️ **একটিভ নম্বর রয়েছে!**\n📞 নম্বর: `{active_order['phone']}`",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return

        services = list(services_col.find({}))
        if not services:
            await update.message.reply_text("❌ বর্তমানে কোনো সার্ভিস চালু নেই।")
            return

        keyboard = [[InlineKeyboardButton(f"{s['flag']} {s['country']} - {s['service']} (${s['rate']})", callback_data=f"buy_{s['_id']}")] for s in services]
        await update.message.reply_text("🛒 **সার্ভিস নির্বাচন করুন:**", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "💳 Deposit (Binance)":
        binance_id = os.getenv("BINANCE_PAY_ID", "123456789")
        await update.message.reply_text(f"💰 **Binance Pay ID:** `{binance_id}`", parse_mode="Markdown")

    elif text == "👤 Profile & Balance":
        await update.message.reply_text(f"👤 **ID:** `{user_id}`\n💵 **Balance:** `${user.get('balance', 0.0):.2f}`", parse_mode="Markdown")

    elif text == "📋 My History":
        history = user.get("history", [])
        if not history:
            await update.message.reply_text("📜 কোনো হিস্ট্রি পাওয়া যায়নি।")
            return
        msg = "📜 **আপনার অর্ডার ইতিহাস:**\n\n" + "\n".join([f"📞 `{item['phone']}` | 💬 OTP: `{item['otp']}`" for item in history[-5:]])
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "❓ Help & Support":
        await update.message.reply_text(f"💬 সহায়তার জন্য যোগাযোগ করুন: {ADMIN_BKASH}")

    elif text == "🔙 Main Menu":
        await start(update, context)

async def handle_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    text = update.message.text
    if text == "👥 View Subscribed History":
        sub_users = list(users_col.find({"is_subscribed": True}))
        if not sub_users:
            await update.message.reply_text("❌ কোনো সাবস্ক্রাইবড ইউজার নেই।")
            return
        msg = "📊 **সাবস্ক্রাইবড ইউজার হিস্ট্রি:**\n\n" + "\n".join([f"👤 {u.get('name')} (`{u['user_id']}`) | Bal: ${u.get('balance', 0.0):.2f}" for u in sub_users])
        await update.message.reply_text(msg, parse_mode="Markdown")

# ----------------- MAIN RUNNER -----------------

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    sub_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💳 সাবস্ক্রিপশন কিনুন \(৳৩০\)$"), start_subscription)],
        states={
            SUB_TRX: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_trx_id)],
            SUB_SS: [MessageHandler(filters.PHOTO, get_screenshot)]
        },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(sub_conv)
    app.add_handler(CallbackQueryHandler(handle_sub_approval, pattern="^sub_"))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_user_menu))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_admin_menu))

    print("🤖 Bot started successfully...")
    app.run_polling(drop_pending_updates=True)