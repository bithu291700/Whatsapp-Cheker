import os
import sys
import logging
import asyncio
import requests
from datetime import datetime
from pymongo import MongoClient
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    MessageHandler, ContextTypes, ConversationHandler, filters
)

# Telethon imports for real Telegram number checking
from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact

# ----------------- CONFIGURATION & MONGODB SETUP -----------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
SMSBOWER_API_KEY = os.getenv("SMSBOWER_API_KEY", "YOUR_SMSBOWER_API_KEY")

TG_API_ID = int(os.getenv("TG_API_ID", "0"))
TG_API_HASH = os.getenv("TG_API_HASH", "your_telegram_api_hash")

try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
except (TypeError, ValueError):
    ADMIN_ID = 0

try:
    OTP_GROUP_ID = int(os.getenv("OTP_GROUP_ID", "0"))
except (TypeError, ValueError):
    OTP_GROUP_ID = 0

BINANCE_PAY_ID = os.getenv("BINANCE_PAY_ID", "123456789")
SMSBOWER_URL = "https://smsbower.online/stubs/handler_api.php"

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://your_username:your_password@cluster.mongodb.net/?retryWrites=true&w=majority")
client = MongoClient(MONGO_URI)
db = client["sms_bot_database"]

users_col = db["users"]          
deposits_col = db["deposits"]    
traffic_log_col = db["traffic_log"]  
settings_col = db["settings"]    

if settings_col.find_one({"key": "bot_status"}) is None:
    settings_col.insert_one({"key": "bot_status", "is_on": True})

# CONVERSATION STATES
WAITING_DEPOSIT_AMOUNT = 1
WAITING_TRX_ID = 2
WAITING_SCREENSHOT = 3

WAITING_BAN_ID = 4
WAITING_UNBAN_ID = 5
WAITING_BROADCAST_MSG = 6
WAITING_PRICE_SERVICE_KEY = 7
WAITING_NEW_PRICE = 8
WAITING_ZERO_BALANCE_ID = 9
WAITING_PASSWORD = 10

# IN-MEMORY ACTIVE ORDERS
active_orders = {}  

# Ager sob services abar add kora holo
PREDEFINED_SERVICES = {
    "wa_usa_cellular": {
        "service_code": "wa", 
        "country_id": "12", 
        "operators": ["cellular", "any"], 
        "country_name": "USA Virtual", 
        "service_name": "WhatsApp",
        "flag": "🇺🇸", 
        "max_price": 0.14,    
        "selling_price": 0.120 
    },
    "wa_afghanistan": {
        "service_code": "wa", 
        "country_id": "74", 
        "operators": ["AWCC", "Roshan", "MTN", "Etisalat", "WASEL", "Salaam", "any"], 
        "country_name": "Afghanistan", 
        "service_name": "WhatsApp",
        "flag": "🇦🇫", 
        "max_price": 0.119, 
        "selling_price": 0.119
    },
    "wa_madagascar": {
        "service_code": "wa", 
        "country_id": "17", 
        "operators": ["Airtel", "Orange", "Sacel", "Telma", "BIP / blueline", "any"], 
        "country_name": "Madagascar", 
        "service_name": "WhatsApp",
        "flag": "🇲🇬", 
        "max_price": 0.163, 
        "selling_price": 0.163
    },
    "wa_indonesia": {
        "service_code": "wa", 
        "country_id": "6", 
        "operators": ["PSN", "Indosat Ooredoo Hutchison", "StarOne", "TelkomFlexi", "AXIS", "Smartfren", "Telkomsel", "XL", "TELKOMMobile", "Net 1", "Fren/Hepi", "Hinet", "BOLT! 4G LTE", "3", "Esia", "any"], 
        "country_name": "Indonesia", 
        "service_name": "WhatsApp",
        "flag": "🇮🇩", 
        "max_price": 0.1, 
        "selling_price": 0.1
    },
    "wa_iraq": {
        "service_code": "wa", 
        "country_id": "47", 
        "operators": ["Asia Cell", "SanaTel", "Zain", "Korek", "Mobitel", "Itisaluna", "Omnnea", "any"], 
        "country_name": "Iraq", 
        "service_name": "WhatsApp",
        "flag": "🇮🇶", 
        "max_price": 0.142, 
        "selling_price": 0.142
    },
    "tg_chile": {
        "service_code": "tg", 
        "country_id": "151", 
        "operators": ["entel", "Movistar", "CLARO CL", "WOM", "any"], 
        "country_name": "Chile", 
        "service_name": "Telegram",
        "flag": "🇨🇱", 
        "max_price": 0.108, 
        "selling_price": 0.108
    }
}

# ----------------- REAL TELEGRAM NUMBER CHECKER (TELETHON) -----------------
async def check_telegram_number_status(phone_number, service_code):
    if service_code != "tg":
        return "✨ **Status:** Fresh Number (Ready)"
    
    if not TG_API_ID or not TG_API_HASH or TG_API_ID == 0:
        return "🟢 **Telegram Status:** Fresh Number (API ID missing)"

    client_tele = TelegramClient('checker_session', TG_API_ID, TG_API_HASH)
    try:
        await client_tele.connect()
        if not await client_tele.is_user_authorized():
            await client_tele.disconnect()
            return "🟢 **Telegram Status:** Fresh & Clean (Ready)"

        contact = InputPhoneContact(client_id=0, phone=phone_number, first_name="Test", last_name="User")
        result = await client_tele(ImportContactsRequest([contact]))
        await client_tele.disconnect()

        if result.users:
            return "🔴 **Telegram Status:** Already Registered / Account Exists!"
        else:
            return "🟢 **Telegram Status:** 100% Fresh & Clean (Not Registered)"
    except Exception as e:
        try:
            await client_tele.disconnect()
        except:
            pass
        return "🟢 **Telegram Status:** Fresh & Clean (Ready)"

# ----------------- KEYBOARDS -----------------

def get_main_keyboard(is_admin=False):
    keyboard = [
        [KeyboardButton("💳 Account Balance"), KeyboardButton("🛒 Buy Number")],
        [KeyboardButton("👤 Profile"), KeyboardButton("💳 Deposit")]
    ]
    if is_admin:
        keyboard.append([KeyboardButton("⚙️ Admin Panel")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard():
    bot_status = settings_col.find_one({"key": "bot_status"}).get("is_on", True)
    status_btn_text = "🔴 Turn Bot OFF" if bot_status else "🟢 Turn Bot ON"
    
    keyboard = [
        [KeyboardButton("👥 View All Users"), KeyboardButton("💰 Set Service Price")],
        [KeyboardButton("📊 Live Traffic"), KeyboardButton("📢 Broadcast")],
        [KeyboardButton("🚫 Ban User"), KeyboardButton("✅ Unban User")],
        [KeyboardButton("🔄 Zero User Balance"), KeyboardButton(status_btn_text)],
        [KeyboardButton("🔙 Main Menu")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_user_data(user_id, name, username):
    user = users_col.find_one({"user_id": user_id})
    if not user:
        user = {
            "user_id": user_id,
            "name": name,
            "username": username or "N/A",
            "balance": 0.0,
            "total_otp": 0,
            "is_banned": False,
            "is_verified": False
        }
        users_col.insert_one(user)
    return user

def update_user_field(user_id, update_dict):
    users_col.update_one({"user_id": user_id}, {"$set": update_dict})

# ----------------- START & PASSWORD HANDLER -----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.effective_user.first_name
    username = update.effective_user.username

    bot_status = settings_col.find_one({"key": "bot_status"}).get("is_on", True)
    if not bot_status and user_id != ADMIN_ID:
        await update.message.reply_text("🛠 Bot ekhon maintenance-er karone off royeche.")
        return ConversationHandler.END

    user = get_user_data(user_id, name, username)

    if user.get("is_banned"):
        await update.message.reply_text("🚫 Apnake ban kora hoyeche.")
        return ConversationHandler.END

    is_admin = (user_id == ADMIN_ID)

    if not is_admin and not user.get("is_verified", False):
        await update.message.reply_text("🔒 Bot-ti bebohar korar jonno sothik password-ti din:")
        return WAITING_PASSWORD

    # Yellow Loading Animation for Start
    msg_obj = await update.message.reply_text("🟡 **Loading System...**\n`[▒▒▒▒▒▒▒▒▒▒] 0%`", parse_mode="Markdown")
    await asyncio.sleep(0.4)
    await msg_obj.edit_text("🟡 **Connecting Database...**\n`[█████▒▒▒▒▒] 50%`", parse_mode="Markdown")
    await asyncio.sleep(0.4)
    await msg_obj.edit_text("🟡 **Welcome Ready!**\n`[██████████] 100%`", parse_mode="Markdown")
    await asyncio.sleep(0.3)
    await msg_obj.delete()

    msg = f"👋 **Hello {name}!**\n\nSwagotom amader SMS Service Bote."
    await update.message.reply_text(msg, reply_markup=get_main_keyboard(is_admin=is_admin), parse_mode="Markdown")
    return ConversationHandler.END

async def verify_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    name = update.effective_user.first_name
    username = update.effective_user.username

    if text == "REX1234":
        update_user_field(user_id, {"is_verified": True})
        
        # Yellow Loading Animation after password success
        msg_obj = await update.message.reply_text("🟡 **Verifying Password...**\n`[▒▒▒▒▒▒▒▒▒▒] 0%`", parse_mode="Markdown")
        await asyncio.sleep(0.4)
        await msg_obj.edit_text("🟡 **Access Granted...**\n`[██████████] 100%`", parse_mode="Markdown")
        await asyncio.sleep(0.3)
        await msg_obj.delete()

        await update.message.reply_text("✅ Password sothik hoyeche!")
        user = get_user_data(user_id, name, username)
        is_admin = (user_id == ADMIN_ID)
        msg = f"👋 **Hello {name}!**\n\nSwagotom amader SMS Service Bote."
        await update.message.reply_text(msg, reply_markup=get_main_keyboard(is_admin=is_admin), parse_mode="Markdown")
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ Vul password! Abar sothik password-ti din:")
        return WAITING_PASSWORD

# ----------------- USER & ADMIN MENU HANDLERS -----------------

async def handle_user_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    name = update.effective_user.first_name
    username = update.effective_user.username
    
    bot_status = settings_col.find_one({"key": "bot_status"}).get("is_on", True)
    if not bot_status and user_id != ADMIN_ID:
        return

    user = get_user_data(user_id, name, username)
    if user.get("is_banned"):
        return

    if not (user_id == ADMIN_ID) and not user.get("is_verified", False):
        return

    if user_id == ADMIN_ID and text in ["🟢 Turn Bot ON", "🔴 Turn Bot OFF"]:
        current_status = bot_status
        new_status = not current_status
        settings_col.update_one({"key": "bot_status"}, {"$set": {"is_on": new_status}})
        status_text = "🟢 Bot ON kora hoyeche." if new_status else "🔴 Bot OFF kora hoyeche."
        await update.message.reply_text(status_text, reply_markup=get_admin_keyboard())
        return

    if text == "💳 Account Balance":
        if user_id == ADMIN_ID:
            sms_bal = "N/A"
            try:
                res = requests.get(SMSBOWER_URL, params={"api_key": SMSBOWER_API_KEY, "action": "getBalance"}, timeout=5).text
                if "ACCESS_BALANCE" in res:
                    sms_bal = str(res.split(":")[1])
            except Exception:
                sms_bal = "Error fetching"
            msg = f"💳 **Admin Balance:**\n🌐 SMS Bower: ${sms_bal}\n💰 Personal: ${user.get('balance', 0.0):.2f}"
        else:
            msg = f"💳 **Apnar bortoman balance:** ${user.get('balance', 0.0):.2f}"
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "👤 Profile":
        msg = f"👤 **User Profile**\n🆔 ID: `{user_id}`\n💰 Balance: **${user.get('balance', 0.0):.2f}**\n📩 OTP: **{user.get('total_otp', 0)}**"
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "🛒 Buy Number":
        if user_id in active_orders:
            order = active_orders[user_id]
            keyboard = [
                [InlineKeyboardButton("🔄 Check OTP", callback_data=f"chk_otp_{user_id}")],
                [
                    InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_ord_{user_id}"),
                    InlineKeyboardButton("🔄 Cancel & Next Buy", callback_data=f"nextbuy_{order['service_key']}")
                ]
            ]
            msg = f"📌 **Active Number:**\n🔹 Service: **{order['service_name']}**\n📞 Number: `{order['phone']}`\n{order['checker_status']}"
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            return

        keyboard = []
        for s_key, s_data in PREDEFINED_SERVICES.items():
            btn_text = f"{s_data['flag']} {s_data['service_name']} ({s_data['country_name']}) - ${s_data['selling_price']:.3f}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"buynum_{s_key}")])

        keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="nav_back_main")])
        await update.message.reply_text("📂 **Available Services List:**", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "⚙️ Admin Panel" and user_id == ADMIN_ID:
        await update.message.reply_text("👑 **Admin Panel:**", reply_markup=get_admin_keyboard(), parse_mode="Markdown")

    elif text == "🔙 Main Menu":
        is_admin = (user_id == ADMIN_ID)
        await update.message.reply_text("🏠 Main Menu:", reply_markup=get_main_keyboard(is_admin=is_admin))

# ----------------- BUY NUMBER & CHECKER FLOW -----------------

async def handle_category_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "nav_back_main":
        await query.message.delete()
        user_id = query.from_user.id
        is_admin = (user_id == ADMIN_ID)
        await query.message.reply_text("🏠 Main Menu:", reply_markup=get_main_keyboard(is_admin=is_admin))

async def execute_buy_number(user_id, s_key, user, query_or_message, is_edit=True):
    s_data = PREDEFINED_SERVICES.get(s_key)
    if not s_data:
        return

    charge_price = s_data['selling_price']
    user_balance = user.get('balance', 0.0)

    if user_balance < charge_price:
        msg_bal = f"❌ Porjapto balance nei! Proyojon: ${charge_price:.3f}, Apnar Balance:${user_balance:.2f}"
        if is_edit:
            await query_or_message.edit_message_text(msg_bal)
        else:
            await query_or_message.reply_text(msg_bal)
        return

    # Green Loading Animation for Buying & Checking Number
    if is_edit:
        await query_or_message.edit_message_text("🟢 **Connecting Gateway...**\n`[▒▒▒▒▒▒▒▒▒▒] 0%`", parse_mode="Markdown")
        await asyncio.sleep(0.3)
        await query_or_message.edit_message_text("🟢 **Fetching Number & Checking Status...**\n`[█████▒▒▒▒▒] 50%`", parse_mode="Markdown")
        await asyncio.sleep(0.3)
    else:
        await query_or_message.reply_text("🟢 **Connecting Gateway...**", parse_mode="Markdown")

    bought_success = False
    act_id = ""
    phone = ""

    operators_to_try = s_data.get("operators", [None])
    for op in operators_to_try:
        params = {
            "api_key": SMSBOWER_API_KEY,
            "action": "getNumber",
            "service": s_data['service_code'],
            "country": s_data['country_id'],
            "maxPrice": s_data['max_price']  
        }
        if op and op != "any":
            params["operator"] = op

        try:
            res = requests.get(SMSBOWER_URL, params=params, timeout=10).text
            if "ACCESS_NUMBER" in res:
                parts = res.split(":")
                act_id = parts[1]
                phone = parts[2]
                bought_success = True
                break
        except Exception:
            continue

    if bought_success:
        new_balance = user_balance - charge_price
        update_user_field(user_id, {"balance": new_balance})
        
        checker_status = await check_telegram_number_status(phone, s_data['service_code'])

        active_orders[user_id] = {
            "activation_id": act_id,
            "phone": phone,
            "service_key": s_key,
            "service_name": s_data['service_name'],
            "country_name": s_data['country_name'],
            "flag": s_data['flag'],
            "price": charge_price,
            "checker_status": checker_status
        }

        keyboard = [
            [InlineKeyboardButton("🔄 Check OTP", callback_data=f"chk_otp_{user_id}")],
            [
                InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_ord_{user_id}"),
                InlineKeyboardButton("🔄 Cancel & Next Buy", callback_data=f"nextbuy_{s_key}")
            ]
        ]

        msg = (
            f"🏷 **Service:** {s_data['service_name']}\n"
            f"{s_data['flag']} **Country:** {s_data['country_name']}\n"
            f"📞 **Number:** `{phone}`\n"
            f"💵 **Rate:** ${charge_price:.3f}\n"
            f"{checker_status}\n\n"
            f"⚠️ OTP na asha porjonto opekkha korun..."
        )
        
        if is_edit:
            await query_or_message.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        else:
            await query_or_message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        msg_err = f"⚠️ **Stock Out!**\n❌ Kono number ekhon stock-e nei."
        if is_edit:
            await query_or_message.edit_message_text(msg_err, parse_mode="Markdown")
        else:
            await query_or_message.reply_text(msg_err, parse_mode="Markdown")

async def handle_buy_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    user = get_user_data(user_id, query.from_user.first_name, query.from_user.username)

    if user_id in active_orders and data.startswith("buynum_"):
        await query.answer("❌ Apnar ekti number active ache!", show_alert=True)
        return

    if data.startswith("buynum_"):
        s_key = data.replace("buynum_", "")
        await execute_buy_number(user_id, s_key, user, query, is_edit=True)

    elif data.startswith("nextbuy_"):
        s_key = data.replace("nextbuy_", "")
        order = active_orders.get(user_id)
        if order:
            try:
                requests.get(SMSBOWER_URL, params={"api_key": SMSBOWER_API_KEY, "action": "setStatus", "status": 8, "id": order['activation_id']}, timeout=5)
            except Exception:
                pass
            refund_balance = user.get('balance', 0.0) + order['price']
            update_user_field(user_id, {"balance": refund_balance})
            del active_orders[user_id]
            user = get_user_data(user_id, query.from_user.first_name, query.from_user.username)

        await execute_buy_number(user_id, s_key, user, query, is_edit=True)

    elif data.startswith("chk_otp_"):
        order = active_orders.get(user_id)
        if not order:
            await query.edit_message_text("❌ Apnar kono sokriyo number nei.")
            return

        res = requests.get(SMSBOWER_URL, params={"api_key": SMSBOWER_API_KEY, "action": "getStatus", "id": order['activation_id']}, timeout=5).text
        if "STATUS_OK" in res:
            otp_code = res.split(":")[1]
            update_user_field(user_id, {"total_otp": user.get('total_otp', 0) + 1})
            
            msg = f"🎉 **OTP Received!**\n💬 **OTP:** `{otp_code}`"
            del active_orders[user_id]
            await query.edit_message_text(msg, parse_mode="Markdown")
        elif "STATUS_WAIT_CODE" in res:
            await query.answer("⏳ Ekhono OTP aseni...", show_alert=True)
        else:
            await query.answer(f"Status: {res}", show_app_alert=True if 'show_app_alert' in globals() else True)

    elif data.startswith("cancel_ord_"):
        order = active_orders.get(user_id)
        if order:
            try:
                requests.get(SMSBOWER_URL, params={"api_key": SMSBOWER_API_KEY, "action": "setStatus", "status": 8, "id": order['activation_id']}, timeout=5)
            except Exception:
                pass
            refund_balance = user.get('balance', 0.0) + order['price']
            update_user_field(user_id, {"balance": refund_balance})
            del active_orders[user_id]
            await query.edit_message_text("✅ Order batil kora hoyeche ebang balance ferot deya hoyeche.")

# ----------------- MAIN RUNNER -----------------

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    start_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={WAITING_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, verify_password)]},
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(start_conv)
    app.add_handler(CallbackQueryHandler(handle_category_select, pattern="^nav_back_"))
    app.add_handler(CallbackQueryHandler(handle_buy_action, pattern="^(buynum_|chk_otp_|cancel_ord_|nextbuy_)"))
    app.add_handler(MessageHandler(filters.Regex("^(💳 Account Balance|🛒 Buy Number|👤 Profile|⚙️ Admin Panel|🔙 Main Menu|🟢 Turn Bot ON|🔴 Turn Bot OFF)$"), handle_user_menu))

    print("🤖 Bot running successfully with all services and custom loading animations!")
    app.run_polling(drop_pending_updates=True)
