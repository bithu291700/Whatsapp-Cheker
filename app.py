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

# ----------------- IN-MEMORY STORAGE -----------------
users = {}          # {user_id: {name, username, balance, total_otp, is_banned}}
services = {}       # {service_key: {service_name, service_code, country_id, country_name, flag, custom_price, max_price}}
active_orders = {}  # {user_id: {activation_id, phone, service_key, price, start_time}}
deposits = {}       # {deposit_id: {user_id, amount, trx_id, photo_id, status}}
traffic_log = []    # [{timestamp, service_name, country_name}]

# Country Mapping (ID to Name & Flag)
COUNTRY_MAP = {
    "0": {"name": "Russia", "flag": "🇷🇺"},
    "1": {"name": "Ukraine", "flag": "🇺🇦"},
    "2": {"name": "Kazakhstan", "flag": "🇰🇿"},
    "3": {"name": "China", "flag": "🇨🇳"},
    "4": {"name": "Philippines", "flag": "🇵🇭"},
    "5": {"name": "Myanmar", "flag": "🇲🇲"},
    "6": {"name": "Indonesia", "flag": "🇮🇩"},
    "7": {"name": "Malaysia", "flag": "🇲🇾"},
    "8": {"name": "Kenya", "flag": "🇰🇪"},
    "9": {"name": "Vietnam", "flag": "🇻🇳"},
    "10": {"name": "Kyrgyzstan", "flag": "🇰🇬"},
    "12": {"name": "USA", "flag": "🇺🇸"},
    "13": {"name": "Israel", "flag": "🇮🇱"},
    "14": {"name": "Hong Kong", "flag": "🇭🇰"},
    "15": {"name": "Poland", "flag": "🇵🇱"},
    "16": {"name": "England", "flag": "🇬🇧"},
    "22": {"name": "India", "flag": "🇮🇳"},
    "73": {"name": "Brazil", "flag": "🇧🇷"}
}

# ----------------- KEYBOARDS -----------------

def get_main_keyboard(is_admin=False):
    keyboard = [
        [KeyboardButton("💳 Account Balance"), KeyboardButton("🛒 Buy Number")],
        [KeyboardButton("🌐 Set Country"), KeyboardButton("🛠 Set Service")],
        [KeyboardButton("👤 Profile"), KeyboardButton("💳 Deposit")]
    ]
    if is_admin:
        keyboard.append([KeyboardButton("⚙️ Admin Panel")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard():
    keyboard = [
        [KeyboardButton("👥 View All Users"), KeyboardButton("➕ Add Service")],
        [KeyboardButton("💰 Set Service Price"), KeyboardButton("📊 Live Traffic")],
        [KeyboardButton("🚫 Ban User"), KeyboardButton("✅ Unban User")],
        [KeyboardButton("📢 Broadcast"), KeyboardButton("🔙 Main Menu")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_user_data(user_id, name, username):
    if user_id not in users:
        users[user_id] = {
            "name": name,
            "username": username or "N/A",
            "balance": 0.0,
            "total_otp": 0,
            "is_banned": False
        }
    return users[user_id]

# ----------------- START HANDLER -----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.effective_user.first_name
    username = update.effective_user.username

    user = get_user_data(user_id, name, username)

    if user["is_banned"]:
        await update.message.reply_text("🚫 আপনাকে বোটে ব্যান করা হয়েছে।")
        return

    is_admin = (user_id == ADMIN_ID)
    msg = "👋 **হ্যালো {}!**\n\nস্বাগতম আমাদের সার্ভিস বোটে।".format(name)
    await update.message.reply_text(msg, reply_markup=get_main_keyboard(is_admin=is_admin), parse_mode="Markdown")

# ----------------- USER MENU HANDLERS -----------------

async def handle_user_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    name = update.effective_user.first_name
    username = update.effective_user.username
    user = get_user_data(user_id, name, username)

    if user["is_banned"]:
        return

    # 1. ACCOUNT BALANCE
    if text == "💳 Account Balance":
        if user_id == ADMIN_ID:
            sms_bal = "N/A"
            try:
                res = requests.get(SMSBOWER_URL, params={"api_key": SMSBOWER_API_KEY, "action": "getBalance"}, timeout=5).text
                if "ACCESS_BALANCE" in res:
                    sms_bal = str(res.split(":")[1])
            except Exception:
                sms_bal = "Error fetching"

            total_user_bal = sum(u["balance"] for u in users.values())
            msg = (
                "💳 **অ্যাডমিন অ্যাকাউন্ট ব্যালেন্স & ইনফো:**\n\n"
                "🌐 **SMS Bower API Balance:** ${}\n"
                "👥 **Total Bot Users:** {}\n"
                "💰 **Total User Balances:** ${:.2f}"
            ).format(sms_bal, len(users), total_user_bal)
        else:
            msg = "💳 **আপনার বর্তমান ব্যালেন্স:** ${:.2f}".format(user['balance'])
        
        await update.message.reply_text(msg, parse_mode="Markdown")

    # 2. PROFILE
    elif text == "👤 Profile":
        msg = (
            "👤 **ইউজার প্রোফাইল**\n\n"
            "🆔 ID: `{}`\n"
            "👤 Name: {}\n"
            "💰 Balance: **${:.2f}**\n"
            "📩 Total OTP Received: **{}**"
        ).format(user_id, user['name'], user['balance'], user['total_otp'])
        await update.message.reply_text(msg, parse_mode="Markdown")

    # 3. ADMIN PANEL
    elif text == "⚙️ Admin Panel":
        if user_id == ADMIN_ID:
            await update.message.reply_text("👑 **অ্যাডমিন প্যানেলে স্বাগতম!**", reply_markup=get_admin_keyboard(), parse_mode="Markdown")

    elif text == "🔙 Main Menu":
        await start(update, context)

    # 4. BUY NUMBER
    elif text == "🛒 Buy Number":
        if user_id in active_orders:
            order = active_orders[user_id]
            keyboard = [
                [InlineKeyboardButton("🔄 Check OTP", callback_data="chk_otp_" + str(user_id))],
                [InlineKeyboardButton("❌ Cancel Order", callback_data="cancel_ord_" + str(user_id))]
            ]
            msg = (
                "📌 **আপনার একটি নাম্বার অ্যাক্টিভ আছে!**\n\n"
                "🔹 Service: **{}**\n"
                "{} Country: **{}**\n"
                "📞 Number: `{}`"
            ).format(order['service_name'], order['flag'], order['country_name'], order['phone'])
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            return

        if not services:
            await update.message.reply_text("❌ বর্তমানে কোনো সার্ভিস অ্যাড করা নেই।")
            return

        keyboard = []
        for key, s_data in services.items():
            btn_text = "{} {} - {} (${:.2f})".format(s_data['flag'], s_data['country_name'], s_data['service_name'], s_data['custom_price'])
            keyboard.append([InlineKeyboardButton(btn_text, callback_data="buynum_" + str(key))])

        await update.message.reply_text("🛒 **একটি সার্ভিস সিলেক্ট করুন:**", reply_markup=InlineKeyboardMarkup(keyboard))

# ----------------- ADD SERVICE -----------------

async def admin_add_service_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        [InlineKeyboardButton("✈️ Telegram", callback_data="addcat_tg"), InlineKeyboardButton("💬 WhatsApp", callback_data="addcat_wa")]
    ]
    await update.message.reply_text("📂 **কোন ক্যাটাগরির সার্ভিস অ্যাড করতে চান সিলেক্ট করুন:**", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_category_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("addcat_"):
        code = data.replace("addcat_", "")
        service_name = "Telegram" if code == "tg" else "WhatsApp"

        params = {"api_key": SMSBOWER_API_KEY, "action": "getPrices", "service": code}
        
        try:
            res = requests.get(SMSBOWER_URL, params=params, timeout=10).json()
            keyboard = []
            for cid, cinfo in COUNTRY_MAP.items():
                if cid in res and code in res[cid]:
                    cost = float(res[cid][code].get("cost", 0))
                    count = res[cid][code].get("count", 0)
                    
                    s_key = "{}_{}".format(code, cid)
                    status = "✅ Added" if s_key in services else "➕ Add"
                    
                    btn_text = "{} {} - {} (${}) [Stock: {}] [{}]".format(cinfo['flag'], cinfo['name'], service_name, cost, count, status)
                    cb_data = "save_s_{}_{}".format(s_key, cost)
                    keyboard.append([InlineKeyboardButton(btn_text, callback_data=cb_data)])

            if not keyboard:
                await query.edit_message_text("❌ কোনো কান্ট্রি/স্টক পাওয়া যায়নি।")
                return

            await query.edit_message_text("🌐 **{} এর A to Z কান্ট্রি লিস্ট (Stock & Price সহ):**".format(service_name), reply_markup=InlineKeyboardMarkup(keyboard))

        except Exception as err:
            await query.edit_message_text("❌ API data fetch error: " + str(err))

async def handle_save_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("save_s_"):
        parts = data.split("_")
        code = parts[2]
        cid = parts[3]
        cost = float(parts[4])

        s_key = "{}_{}".format(code, cid)
        cinfo = COUNTRY_MAP.get(cid, {"name": "Unknown", "flag": "🏳️"})
        service_name = "Telegram" if code == "tg" else "WhatsApp"

        selling_price = cost + 0.10
        max_limit = cost + 0.50

        services[s_key] = {
            "service_name": service_name,
            "service_code": code,
            "country_id": cid,
            "country_name": cinfo['name'],
            "flag": cinfo['flag'],
            "cost_price": cost,
            "custom_price": selling_price,
            "max_price": max_limit
        }

        # SAFE FORMATTING WITHOUT F-STRING SYNTAX ISSUES
        msg = (
            "✅ **{} {} - {}** অ্যাড করা হয়েছে!\n"
            "💵 Cost: ${:.2f} | Selling Price: ${:.2f} \vert{} Max Limit:${:.2f}"
        ).format(cinfo['flag'], cinfo['name'], service_name, cost, selling_price, max_limit)

        await query.edit_message_text(msg, parse_mode="Markdown")

# ----------------- BUY NUMBER & OTP FLOW -----------------

async def handle_buy_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    user = get_user_data(user_id, query.from_user.first_name, query.from_user.username)

    if data.startswith("buynum_"):
        s_key = data.replace("buynum_", "")
        s_data = services.get(s_key)

        if not s_data:
            await query.edit_message_text("❌ সার্ভিস পাওয়া যায়নি।")
            return

        # Max Price Limit Check
        try:
            p_res = requests.get(SMSBOWER_URL, params={"api_key": SMSBOWER_API_KEY, "action": "getPrices", "service": s_data['service_code'], "country": s_data['country_id']}, timeout=5).json()
            current_api_cost = float(p_res.get(s_data['country_id'], {}).get(s_data['service_code'], {}).get("cost", 999))
            
            if current_api_cost > s_data['max_price']:
                msg_limit = "⚠️ **দাম বেশি হওয়ার কারণে ব্লক করা হয়েছে!**\nAPI Cost: ${:.2f}, Max Allowed:${:.2f}".format(current_api_cost, s_data['max_price'])
                await query.edit_message_text(msg_limit, parse_mode="Markdown")
                return
        except Exception:
            pass

        price = s_data['custom_price']
        if user['balance'] < price:
            msg_bal = "❌ পর্যাপ্ত ব্যালেন্স নেই! প্রয়োজন: ${:.2f}, আছে: ${:.2f}".format(price, user['balance'])
            await query.edit_message_text(msg_bal)
            return

        params = {
            "api_key": SMSBOWER_API_KEY,
            "action": "getNumber",
            "service": s_data['service_code'],
            "country": s_data['country_id']
        }

        try:
            res = requests.get(SMSBOWER_URL, params=params, timeout=10).text
            if "ACCESS_NUMBER" in res:
                parts = res.split(":")
                act_id = parts[1]
                phone = parts[2]

                user['balance'] -= price

                active_orders[user_id] = {
                    "activation_id": act_id,
                    "phone": phone,
                    "service_key": s_key,
                    "service_name": s_data['service_name'],
                    "country_name": s_data['country_name'],
                    "flag": s_data['flag'],
                    "price": price
                }

                keyboard = [
                    [InlineKeyboardButton("🔄 Check OTP", callback_data="chk_otp_" + str(user_id))],
                    [InlineKeyboardButton("❌ Cancel Order", callback_data="cancel_ord_" + str(user_id))]
                ]

                msg = (
                    "🏷 **Service:** {}\n"
                    "{} **Country:** {}\n"
                    "📞 **Number:** `{}`\n"
                    "💵 **Rate:** ${:.2f}\n\n"
                    "⚠️ OTP না আসা পর্যন্ত অপেক্ষা করুন..."
                ).format(s_data['service_name'], s_data['flag'], s_data['country_name'], phone, price)
                await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            else:
                msg_err = "❌ নাম্বার পাওয়া যায়নি (Stock Empty)। API: " + str(res)
                await query.edit_message_text(msg_err)
        except Exception as e:
            msg_ex = "❌ API ত্রুটি: " + str(e)
            await query.edit_message_text(msg_ex)

    elif data.startswith("chk_otp_"):
        order = active_orders.get(user_id)
        if not order:
            await query.edit_message_text("❌ আপনার কোনো সক্রিয় নম্বর নেই।")
            return

        res = requests.get(SMSBOWER_URL, params={"api_key": SMSBOWER_API_KEY, "action": "getStatus", "id": order['activation_id']}, timeout=5).text
        if "STATUS_OK" in res:
            otp_code = res.split(":")[1]
            user['total_otp'] += 1
            traffic_log.append({"timestamp": datetime.now(), "service_name": order['service_name'], "country_name": order['country_name']})

            msg = (
                "🎉 **OTP Received!**\n\n"
                "🏷 Service: {}\n"
                "📞 Number: `{}`\n"
                "💬 **OTP:** `{}`"
            ).format(order['service_name'], order['phone'], otp_code)
            del active_orders[user_id]
            await query.edit_message_text(msg, parse_mode="Markdown")
        elif "STATUS_WAIT_CODE" in res:
            await query.answer("⏳ এখনও OTP আসেনি, আবার চেষ্টা করুন...", show_alert=True)
        else:
            await query.answer("Status: " + str(res), show_alert=True)

    elif data.startswith("cancel_ord_"):
        order = active_orders.get(user_id)
        if order:
            try:
                requests.get(SMSBOWER_URL, params={"api_key": SMSBOWER_API_KEY, "action": "setStatus", "status": 8, "id": order['activation_id']}, timeout=5)
            except Exception:
                pass
            user['balance'] += order['price']
            del active_orders[user_id]
            await query.edit_message_text("✅ অর্ডার বাতিল করা হয়েছে এবং ব্যালেন্স ফেরত দেয়া হয়েছে।")

# ----------------- MAIN RUNNER -----------------

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_category_select, pattern="^addcat_"))
    app.add_handler(CallbackQueryHandler(handle_save_service, pattern="^save_s_"))
    app.add_handler(CallbackQueryHandler(handle_buy_action, pattern="^(buynum_|chk_otp_|cancel_ord_)"))

    app.add_handler(MessageHandler(filters.Regex("^(💳 Account Balance|🛒 Buy Number|🌐 Set Country|🛠 Set Service|👤 Profile|💳 Deposit|⚙️ Admin Panel|🔙 Main Menu)$"), handle_user_menu))
    app.add_handler(MessageHandler(filters.Regex("^➕ Add Service$"), admin_add_service_menu))

    print("🤖 Bot is starting cleanly...")
    app.run_polling(drop_pending_updates=True)
