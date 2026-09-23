import os
import sys
import logging
import requests
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    MessageHandler, ContextTypes, ConversationHandler, filters
)

# ----------------- CONFIGURATION -----------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
SMSBOWER_API_KEY = os.getenv("SMSBOWER_API_KEY", "YOUR_SMSBOWER_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
BINANCE_PAY_ID = os.getenv("BINANCE_PAY_ID", "123456789")
SMSBOWER_URL = "https://smsbower.online/stubs/handler_api.php"

# ----------------- IN-MEMORY STORAGE (NO MONGO NEEDED) -----------------
users = {}          # {user_id: {name, username, balance, total_otp, is_subscribed, is_banned}}
services = {}       # {service_id: {service_name, country_code, country_name, flag, cost_price, custom_price}}
active_orders = {}  # {user_id: {activation_id, phone, service_id, price, start_time}}
deposits = {}       # {deposit_id: {user_id, amount, trx_id, photo_id, status}}
traffic_log = []    # [{timestamp, service_name, country_name}]

# States for ConversationHandlers
DEP_AMT, DEP_TRX, DEP_SS = range(3)
ADMIN_SET_PRICE_VAL = 10

# Country Flags Helper Mapping
COUNTRY_FLAGS = {
    "russia": "🇷🇺", "ukraine": "🇺🇦", "kazakhstan": "🇰🇿", "china": "🇨🇳",
    "philippines": "🇵🇭", "myanmar": "🇲🇲", "indonesia": "🇮🇩", "malaysia": "🇲🇾",
    "kenya": "🇰🇪", "vietnam": "🇻🇳", "kyrgyzstan": "🇰🇬", "usa": "🇺🇸",
    "israel": "🇮🇱", "hongkong": "🇭🇰", "poland": "🇵🇱", "england": "🇬🇧",
    "india": "🇮🇳", "brazil": "🇧🇷"
}

# ----------------- KEYBOARDS -----------------

def get_user_keyboard():
    keyboard = [
        [KeyboardButton("📱 Buy Number"), KeyboardButton("👤 Profile")],
        [KeyboardButton("💳 Deposit"), KeyboardButton("📊 Live Traffic")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard():
    keyboard = [
        [KeyboardButton("👥 View All Users"), KeyboardButton("➕ Add Service")],
        [KeyboardButton("💰 Set Service Price"), KeyboardButton("📊 Live Traffic")],
        [KeyboardButton("🚫 Ban User"), KeyboardButton("✅ Unban User")],
        [KeyboardButton("🔙 Main Menu")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ----------------- HELPER FUNCTIONS -----------------

def get_user(user_id, name, username):
    if user_id not in users:
        users[user_id] = {
            "name": name,
            "username": username or "N/A",
            "balance": 0.0,
            "total_otp": 0,
            "is_subscribed": True, # set True for testing
            "is_banned": False
        }
    return users[user_id]

# ----------------- START HANDLER -----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.effective_user.first_name
    username = update.effective_user.username

    user = get_user(user_id, name, username)

    if user["is_banned"]:
        await update.message.reply_text("🚫 আপনাকে বোটে ব্যান করা হয়েছে।")
        return

    if user_id == ADMIN_ID:
        await update.message.reply_text("👑 **অ্যাডমিন প্যানেলে স্বাগতম!**", reply_markup=get_admin_keyboard(), parse_mode="Markdown")
    else:
        msg = f"👋 **হ্যালো {name}!**\n\nস্বাগতম আমাদের সার্ভিস বোটে। নিচের মেনু থেকে অপশন সিলেক্ট করুন।"
        await update.message.reply_text(msg, reply_markup=get_user_keyboard(), parse_mode="Markdown")

# ----------------- USER FEATURES -----------------

async def handle_user_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    name = update.effective_user.first_name
    username = update.effective_user.username
    user = get_user(user_id, name, username)

    if user["is_banned"]:
        return

    # 1. PROFILE
    if text == "👤 Profile":
        msg = (
            f"👤 **ইউজার প্রোফাইল**\n\n"
            f"🆔 ID: `{user_id}`\n"
            f"👤 Name: {user['name']}\n"
            f"💰 Balance: **${user['balance']:.2f}**\n"
            f"📩 Total OTP Received: **{user['total_otp']}**"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    # 2. LIVE TRAFFIC
    elif text == "📊 Live Traffic":
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_logs = [t for t in traffic_log if t['timestamp'] >= one_hour_ago]

        if not recent_logs:
            await update.message.reply_text("📊 **গত ১ ঘণ্টায় কোনো OTP রিসিভ হয়নি।**")
            return

        summary = {}
        for item in recent_logs:
            key = f"{item['country_name']} - {item['service_name']}"
            summary[key] = summary.get(key, 0) + 1

        msg = "📊 **গত ১ ঘণ্টার Live Traffic:**\n\n"
        for key, count in summary.items():
            msg += f"• {key}: **{count} OTPs**\n"

        await update.message.reply_text(msg, parse_mode="Markdown")

    # 3. BUY NUMBER
    elif text == "📱 Buy Number":
        if user_id in active_orders:
            order = active_orders[user_id]
            keyboard = [
                [InlineKeyboardButton("🔄 Check OTP", callback_data=f"chk_otp_{user_id}")],
                [InlineKeyboardButton("❌ Cancel Order", callback_data=f"cancel_ord_{user_id}")]
            ]
            msg = (
                f"📌 **আপনার একটি নাম্বার অ্যাক্টিভ আছে!**\n"
                f"নতুন নাম্বার নেওয়ার আগে বর্তমান কাজ সম্পন্ন বা ক্যানসেল করুন।\n\n"
                f"🔹 Service: **{order['service_name']}**\n"
                f"📞 Number: `{order['phone']}`"
            )
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            return

        if not services:
            await update.message.reply_text("❌ বর্তমানে অ্যাডমিন কর্তৃক কোনো সার্ভিস যুক্ত করা হয়নি।")
            return

        keyboard = []
        for s_id, s_data in services.items():
            btn_text = f"{s_data['flag']} {s_data['country_name']} - {s_data['service_name']} (${s_data['custom_price']:.2f})"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"buynum_{s_id}")])

        await update.message.reply_text("🛒 **একটি সার্ভিস সিলেক্ট করুন:**", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "🔙 Main Menu":
        await start(update, context)

# ----------------- BUY NUMBER & OTP LOGIC -----------------

async def handle_buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    user = get_user(user_id, query.from_user.first_name, query.from_user.username)

    if data.startswith("buynum_"):
        s_id = data.replace("buynum_", "")
        s_data = services.get(s_id)

        if not s_data:
            await query.edit_message_text("❌ সার্ভিসটি পাওয়া যায়নি।")
            return

        price = s_data['custom_price']
        if user['balance'] < price:
            await query.edit_message_text(f"❌ আপনার পর্যাপ্ত ব্যালেন্স নেই! প্রয়োজন: ${price:.2f}, আপনার আছে: ${user['balance']:.2f}")
            return

        # Request Number from SMS Bower API
        # API parameters: api_key, action=getNumber, service, country
        params = {
            "api_key": SMSBOWER_API_KEY,
            "action": "getNumber",
            "service": s_data['service_code'],
            "country": s_data['country_code']
        }

        try:
            res = requests.get(SMSBOWER_URL, params=params, timeout=10).text
            # Response format: ACCESS_NUMBER:id:number
            if "ACCESS_NUMBER" in res:
                parts = res.split(":")
                act_id = parts[1]
                phone = parts[2]

                # Lock balance conceptually (or deduct directly and refund on cancel)
                user['balance'] -= price

                active_orders[user_id] = {
                    "activation_id": act_id,
                    "phone": phone,
                    "service_id": s_id,
                    "service_name": s_data['service_name'],
                    "country_name": s_data['country_name'],
                    "flag": s_data['flag'],
                    "price": price,
                    "start_time": datetime.now()
                }

                keyboard = [
                    [InlineKeyboardButton("🔄 Check OTP", callback_data=f"chk_otp_{user_id}")],
                    [InlineKeyboardButton("❌ Cancel Order", callback_data=f"cancel_ord_{user_id}")]
                ]

                msg = (
                    f"🏷 **Service:** {s_data['service_name']}\n"
                    f"{s_data['flag']} **Country:** {s_data['country_name']}\n"
                    f"📞 **Number:** `{phone}`\n"
                    f"💵 **Rate:** ${price:.2f}\n\n"
                    f"⚠️ OTP আসা পর্যন্ত অপেক্ষা করুন..."
                )
                await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

            else:
                await query.edit_message_text(f"❌ নাম্বার পাওয়া যায়নি। API Response: {res}")
        except Exception as e:
            await query.edit_message_text(f"❌ API এর সাথে যোগাযোগ করা যায়নি: {str(e)}")

    elif data.startswith("chk_otp_"):
        order = active_orders.get(user_id)
        if not order:
            await query.edit_message_text("❌ আপনার কোনো সক্রিয় নাম্বার নেই।")
            return

        params = {
            "api_key": SMSBOWER_API_KEY,
            "action": "getStatus",
            "id": order['activation_id']
        }

        try:
            res = requests.get(SMSBOWER_URL, params=params, timeout=10).text
            # Response: STATUS_OK:code or STATUS_WAIT_CODE
            if "STATUS_OK" in res:
                otp_code = res.split(":")[1]
                user['total_otp'] += 1

                # Log for Live Traffic
                traffic_log.append({
                    "timestamp": datetime.now(),
                    "service_name": order['service_name'],
                    "country_name": order['country_name']
                })

                msg = (
                    f"🎉 **OTP Received!**\n\n"
                    f"🏷 Service: {order['service_name']}\n"
                    f"📞 Number: `{order['phone']}`\n"
                    f"💬 **OTP:** `{otp_code}`"
                )
                del active_orders[user_id]
                await query.edit_message_text(msg, parse_mode="Markdown")

            elif "STATUS_WAIT_CODE" in res:
                await query.answer("⏳ এখনও OTP আসেনি, পুনরায় চেষ্টা করুন...", show_alert=True)
            else:
                await query.answer(f"Status: {res}", show_alert=True)
        except Exception as e:
            await query.answer(f"Error checking status: {str(e)}", show_alert=True)

    elif data.startswith("cancel_ord_"):
        order = active_orders.get(user_id)
        if not order:
            await query.edit_message_text("❌ আপনার কোনো সক্রিয় অর্ডার নেই।")
            return

        params = {
            "api_key": SMSBOWER_API_KEY,
            "action": "setStatus",
            "status": 8, # 8 means cancel
            "id": order['activation_id']
        }

        try:
            requests.get(SMSBOWER_URL, params=params, timeout=10)
        except Exception:
            pass

        # Refund Balance
        user['balance'] += order['price']
        del active_orders[user_id]

        await query.edit_message_text("✅ নাম্বার ক্যানসেল করা হয়েছে এবং আপনার ব্যালেন্স ফেরত দেওয়া হয়েছে।")

# ----------------- DEPOSIT CONVERSATION -----------------

async def start_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        f"💳 **Binance Deposit**\n\n"
        f"🔹 **Binance Pay ID:** `{BINANCE_PAY_ID}`\n"
        f"📌 **Minimum Deposit:** $1.00 USD\n\n"
        f"আপনি কত ডলার ডিপোজিট করতে চান লিখুন (যেমন: 5):"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")
    return DEP_AMT

async def get_deposit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amt = float(update.message.text.strip())
        if amt < 1.0:
            await update.message.reply_text("❌ সর্বনিম্ন ডিপোজিট পরিমাণ $1.00। আবার চেষ্টা করুন:")
            return DEP_AMT
        context.user_data['dep_amt'] = amt
        await update.message.reply_text("🆔 আপনার Binance Transaction ID (TrxID) দিন:")
        return DEP_TRX
    except ValueError:
        await update.message.reply_text("❌ সঠিক সংখ্যা লিখুন (যেমন: 1, 5, 10):")
        return DEP_AMT

async def get_deposit_trx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['dep_trx'] = update.message.text.strip()
    await update.message.reply_text("📸 পেমেন্টের একটি **Screenshot** পাঠান:")
    return DEP_SS

async def get_deposit_ss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    amt = context.user_data.get('dep_amt')
    trx = context.user_data.get('dep_trx')
    photo_id = update.message.photo[-1].file_id

    dep_id = f"dep_{user_id}_{int(datetime.now().timestamp())}"
    deposits[dep_id] = {
        "user_id": user_id,
        "amount": amt,
        "trx_id": trx,
        "photo_id": photo_id,
        "status": "pending"
    }

    await update.message.reply_text("⏳ আপনার ডিপোজিট রিকোয়েস্ট জমা হয়েছে। অ্যাডমিন অনুমোদন করলে ব্যালেন্স যুক্ত হবে।")

    # Notify Admin
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"dep_app_{dep_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"dep_rej_{dep_id}")
        ]
    ]
    admin_msg = (
        f"🔔 **নতুন ডিপোজিট রিকোয়েস্ট!**\n\n"
        f"👤 ইউজার: {user_name} (`{user_id}`)\n"
        f"💰 পরিমাণ: **${amt:.2f}**\n"
        f"🆔 TrxID: `{trx}`"
    )
    if ADMIN_ID != 0:
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=admin_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    return ConversationHandler.END

async def handle_deposit_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    dep_id = data.replace("dep_app_", "").replace("dep_rej_", "")
    dep = deposits.get(dep_id)

    if not dep or dep['status'] != "pending":
        await query.edit_message_caption(caption=f"{query.message.caption}\n\n⚠️ অলরেডি প্রসেস করা হয়েছে।")
        return

    user_id = dep['user_id']
    user = users.get(user_id)

    if "dep_app_" in data:
        dep['status'] = "approved"
        if user:
            user['balance'] += dep['amount']
        await query.edit_message_caption(caption=f"{query.message.caption}\n\n✅ **Approved!**")
        try:
            await context.bot.send_message(user_id, f"🎉 আপনার **${dep['amount']:.2f}** ডিপোজিট সফলভাবে অনুমোদিত হয়েছে!")
        except Exception:
            pass

    elif "dep_rej_" in data:
        dep['status'] = "rejected"
        await query.edit_message_caption(caption=f"{query.message.caption}\n\n❌ **Rejected!**")
        try:
            await context.bot.send_message(user_id, f"❌ আপনার **${dep['amount']:.2f}** ডিপোজিট রিকোয়েস্ট বাতিল করা হয়েছে।")
        except Exception:
            pass

# ----------------- ADMIN PANEL FEATURES -----------------

async def handle_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    text = update.message.text

    # 1. VIEW ALL USERS
    if text == "👥 View All Users":
        if not users:
            await update.message.reply_text("❌ কোনো ইউজার তথ্য পাওয়া যায়নি।")
            return

        msg = "👥 **ইউজারদের তালিকা ও ইতিহাস:**\n\n"
        for uid, udata in users.items():
            msg += f"👤 Name: {udata['name']} (@{udata['username']})\n"
            msg += f"🆔 ID: `{uid}` | 💰 Bal: ${udata['balance']:.2f} | 📩 OTPs: {udata['total_otp']}\n"
            msg += "-------------------------------\n"

        await update.message.reply_text(msg, parse_mode="Markdown")

    # 2. ADD SERVICE (Fetch from SMS Bower for TG & WhatsApp)
    elif text == "➕ Add Service":
        # Predefined mapping for Telegram (tg) and WhatsApp (wa)
        sample_services = [
            {"id": "tg_russia", "name": "Telegram", "code": "tg", "country_code": "0", "country": "Russia", "flag": "🇷🇺", "cost": 0.20},
            {"id": "wa_russia", "name": "WhatsApp", "code": "wa", "country_code": "0", "country": "Russia", "flag": "🇷🇺", "cost": 0.30},
            {"id": "tg_usa", "name": "Telegram", "code": "tg", "country_code": "12", "country": "USA", "flag": "🇺🇸", "cost": 0.25},
            {"id": "wa_usa", "name": "WhatsApp", "code": "wa", "country_code": "12", "country": "USA", "flag": "🇺🇸", "cost": 0.35},
            {"id": "tg_indonesia", "name": "Telegram", "code": "tg", "country_code": "6", "country": "Indonesia", "flag": "🇮🇩", "cost": 0.18},
            {"id": "wa_indonesia", "name": "WhatsApp", "code": "wa", "country_code": "6", "country": "Indonesia", "flag": "🇮🇩", "cost": 0.22},
        ]

        keyboard = []
        for s in sample_services:
            status = "✅ Added" if s['id'] in services else "➕ Add"
            keyboard.append([InlineKeyboardButton(f"{s['flag']} {s['country']} - {s['name']} (${s['cost']}) [{status}]", callback_data=f"adm_add_{s['id']}")])

        await update.message.reply_text("➕ **সার্ভিস সিলেক্ট করে ইউজারদের জন্য যুক্ত করুন:**", reply_markup=InlineKeyboardMarkup(keyboard))

    # 3. SET SERVICE PRICE
    elif text == "💰 Set Service Price":
        if not services:
            await update.message.reply_text("❌ কোনো সার্ভিস অ্যাড করা নেই! প্রথমে **➕ Add Service** করুন।")
            return

        keyboard = []
        for s_id, s_data in services.items():
            btn_text = f"{s_data['flag']} {s_data['country_name']} - {s_data['service_name']} (Current: ${s_data['custom_price']:.2f})"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"setprice_{s_id}")])

        await update.message.reply_text("💰 **যে সার্ভিসের দাম পরিবর্তন করতে চান সিলেক্ট করুন:**", reply_markup=InlineKeyboardMarkup(keyboard))

    # 4. BAN / UNBAN
    elif text == "🚫 Ban User":
        await update.message.reply_text("ব্যান করতে লিখুন: `/ban <USER_ID>`", parse_mode="Markdown")
    elif text == "✅ Unban User":
        await update.message.reply_text("আনব্যান করতে লিখুন: `/unban <USER_ID>`", parse_mode="Markdown")

async def handle_admin_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("adm_add_"):
        s_id = data.replace("adm_add_", "")
        # Dummy adding for testing flow
        sample_map = {
            "tg_russia": {"service_name": "Telegram", "service_code": "tg", "country_code": "0", "country_name": "Russia", "flag": "🇷🇺", "cost_price": 0.20, "custom_price": 0.30},
            "wa_russia": {"service_name": "WhatsApp", "service_code": "wa", "country_code": "0", "country_name": "Russia", "flag": "🇷🇺", "cost_price": 0.30, "custom_price": 0.45},
            "tg_usa": {"service_name": "Telegram", "service_code": "tg", "country_code": "12", "country_name": "USA", "flag": "🇺🇸", "cost_price": 0.25, "custom_price": 0.40},
            "wa_usa": {"service_name": "WhatsApp", "service_code": "wa", "country_code": "12", "country_name": "USA", "flag": "🇺🇸", "cost_price": 0.35, "custom_price": 0.50},
            "tg_indonesia": {"service_name": "Telegram", "service_code": "tg", "country_code": "6", "country_name": "Indonesia", "flag": "🇮🇩", "cost_price": 0.18, "custom_price": 0.28},
            "wa_indonesia": {"service_name": "WhatsApp", "service_code": "wa", "country_code": "6", "country_name": "Indonesia", "flag": "🇮🇩", "cost_price": 0.22, "custom_price": 0.32},
        }

        if s_id in sample_map:
            services[s_id] = sample_map[s_id]
            await query.edit_message_text(f"✅ **{sample_map[s_id]['country_name']} - {sample_map[s_id]['service_name']}** ইউজারদের জন্য যুক্ত করা হয়েছে!")

    elif data.startswith("setprice_"):
        s_id = data.replace("setprice_", "")
        context.user_data['edit_service_id'] = s_id
        await query.edit_message_text(f"📝 সার্ভিসটির নতুন মূল্য ($ USD) লিখে মেসেজ পাঠান (যেমন: 0.50):")

async def admin_ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        uid = int(context.args[0])
        if uid in users:
            users[uid]['is_banned'] = True
            await update.message.reply_text(f"🚫 ইউজার `{uid}` ব্যান করা হয়েছে।")
        else:
            await update.message.reply_text("❌ ইউজার পাওয়া যায়নি।")
    except Exception:
        await update.message.reply_text("ইউজ: `/ban <USER_ID>`")

async def admin_unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        uid = int(context.args[0])
        if uid in users:
            users[uid]['is_banned'] = False
            await update.message.reply_text(f"✅ ইউজার `{uid}` আনব্যান করা হয়েছে।")
        else:
            await update.message.reply_text("❌ ইউজার পাওয়া যায়নি।")
    except Exception:
        await update.message.reply_text("ইউজ: `/unban <USER_ID>`")

async def handle_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    s_id = context.user_data.get('edit_service_id')
    if s_id and s_id in services:
        try:
            new_price = float(update.message.text.strip())
            services[s_id]['custom_price'] = new_price
            del context.user_data['edit_service_id']
            await update.message.reply_text(f"✅ **দাম সফলভাবে আপডেট করা হয়েছে:** ${new_price:.2f}")
        except ValueError:
            await update.message.reply_text("❌ সঠিক সংখ্যা লিখুন (যেমন: 0.40):")

# ----------------- MAIN RUNNER -----------------

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    dep_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💳 Deposit$"), start_deposit)],
        states={
            DEP_AMT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_deposit_amount)],
            DEP_TRX: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_deposit_trx)],
            DEP_SS: [MessageHandler(filters.PHOTO, get_deposit_ss)]
        },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ban", admin_ban_cmd))
    app.add_handler(CommandHandler("unban", admin_unban_cmd))

    app.add_handler(dep_conv)

    app.add_handler(CallbackQueryHandler(handle_deposit_approval, pattern="^dep_"))
    app.add_handler(CallbackQueryHandler(handle_buy_callback, pattern="^(buynum_|chk_otp_|cancel_ord_)"))
    app.add_handler(CallbackQueryHandler(handle_admin_callbacks, pattern="^(adm_add_|setprice_)"))

    app.add_handler(MessageHandler(filters.Regex("^(👤 Profile|📊 Live Traffic|📱 Buy Number|🔙 Main Menu)$"), handle_user_menu))
    app.add_handler(MessageHandler(filters.Regex("^(👥 View All Users|➕ Add Service|💰 Set Service Price|🚫 Ban User|✅ Unban User)$"), handle_admin_menu))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_price_input))

    print("🤖 Bot running successfully without MongoDB errors...")
    app.run_polling(drop_pending_updates=True)
