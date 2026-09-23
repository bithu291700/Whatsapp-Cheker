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

# MAXIMUM COST LIMIT FILTERS
MAX_COST_LIMITS = {
    "tg": 0.40,  # Telegram: Maximum $0.40
    "wa": 0.25   # WhatsApp: Maximum $0.25
}

# ----------------- IN-MEMORY STORAGE -----------------
users = {}          # {user_id: {name, username, balance, total_otp, rank, is_banned}}
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
    "187": {"name": "USA Virtual", "flag": "🇺🇸"},
    "13": {"name": "Israel", "flag": "🇮🇱"},
    "14": {"name": "Hong Kong", "flag": "🇭🇰"},
    "15": {"name": "Poland", "flag": "🇵🇱"},
    "16": {"name": "England", "flag": "🇬🇧"},
    "22": {"name": "India", "flag": "🇮🇳"},
    "73": {"name": "Brazil", "flag": "🇧🇷"},
    "11": {"name": "Colombia", "flag": "🇨🇴"},
    "32": {"name": "Romania", "flag": "🇷🇴"},
    "33": {"name": "Colombia", "flag": "🇨🇴"},
    "34": {"name": "Estonia", "flag": "🇪🇪"},
    "36": {"name": "Canada", "flag": "🇨🇦"},
    "43": {"name": "Germany", "flag": "🇩🇪"},
    "52": {"name": "Thailand", "flag": "🇹🇭"},
    "60": {"name": "South Africa", "flag": "🇿🇦"},
    "68": {"name": "Pakistan", "flag": "🇵🇰"},
    "77": {"name": "Mexico", "flag": "🇲🇽"},
    "80": {"name": "France", "flag": "🇫🇷"},
    "86": {"name": "Italy", "flag": "🇮🇹"},
    "87": {"name": "Spain", "flag": "🇪🇸"},
    "101": {"name": "Morocco", "flag": "🇲🇦"},
    "117": {"name": "Portugal", "flag": "🇵🇹"},
    "128": {"name": "Georgia", "flag": "🇬🇪"},
    "148": {"name": "Armenia", "flag": "🇦🇲"},
    "151": {"name": "Chile", "flag": "🇨🇱"},
    "155": {"name": "Czech Republic", "flag": "🇨🇿"},
    "161": {"name": "Uzbekistan", "flag": "🇺🇿"},
    "165": {"name": "Saudi Arabia", "flag": "🇸🇦"},
    "173": {"name": "Tunisia", "flag": "🇹🇳"},
    "174": {"name": "Moldova", "flag": "🇲🇩"},
    "175": {"name": "Kuwait", "flag": "🇰🇼"},
    "176": {"name": "Slovenia", "flag": "🇸🇮"},
    "177": {"name": "Denmark", "flag": "🇩🇰"},
    "178": {"name": "Austria", "flag": "🇦🇹"},
    "179": {"name": "Afghanistan", "flag": "🇦🇫"},
    "180": {"name": "Chad", "flag": "🇹🇩"},
    "181": {"name": "Finland", "flag": "🇫🇮"},
    "182": {"name": "Lebanon", "flag": "🇱🇧"},
    "183": {"name": "Jamaica", "flag": "🇯🇲"},
    "184": {"name": "New Zealand", "flag": "🇳🇿"},
    "185": {"name": "Iraq", "flag": "🇮🇶"},
    "186": {"name": "Iran", "flag": "🇮🇷"},
    "188": {"name": "Cameroon", "flag": "🇨🇲"},
    "189": {"name": "Nigeria", "flag": "🇳🇬"}
}

def get_country_info(cid):
    cid_str = str(cid)
    if cid_str in COUNTRY_MAP:
        return COUNTRY_MAP[cid_str]
    return {"name": "Country " + cid_str, "flag": "🌐"}

# ----------------- RANK & DISCOUNT SYSTEM -----------------

def get_discounted_price(base_price: float, rank: str) -> float:
    discounts = {
        "Normal": 0.0,
        "Bronze": 0.02,
        "Silver": 0.05,
        "Gold": 0.10
    }
    discount = discounts.get(rank, 0.0)
    return round(base_price * (1.0 - discount), 3)

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
            "rank": "Normal",
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
        await update.message.reply_text("🚫 Apnake bote ban kora hoyeche.")
        return

    is_admin = (user_id == ADMIN_ID)
    msg = "👋 **Hello {}!**\n\nSwagotom amader service bote.\n\n🏆 Apnar Rank: **{}**".format(name, user['rank'])
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
                "💳 **Admin Account Balance & Info:**\n\n"
                "🌐 **SMS Bower API Balance:** ${}\n"
                "👥 **Total Bot Users:** {}\n"
                "💰 **Total User Balances:** ${:.2f}"
            ).format(sms_bal, len(users), total_user_bal)
        else:
            msg = "💳 **Apnar bortoman balance:** ${:.2f}".format(user['balance'])
        
        await update.message.reply_text(msg, parse_mode="Markdown")

    # 2. PROFILE
    elif text == "👤 Profile":
        msg = (
            "👤 **User Profile**\n\n"
            "🆔 ID: `{}`\n"
            "👤 Name: {}\n"
            "🏆 Rank: **{}**\n"
            "💰 Balance: **${:.2f}**\n"
            "📩 Total OTP Received: **{}**"
        ).format(user_id, user['name'], user['rank'], user['balance'], user['total_otp'])
        await update.message.reply_text(msg, parse_mode="Markdown")

    # 3. ADMIN PANEL
    elif text == "⚙️ Admin Panel":
        if user_id == ADMIN_ID:
            await update.message.reply_text("👑 **Admin Panele Swagotom!**", reply_markup=get_admin_keyboard(), parse_mode="Markdown")

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
                "📌 **Apnar ekti number active ache!**\n\n"
                "🔹 Service: **{}**\n"
                "{} Country: **{}**\n"
                "📞 Number: `{}`"
            ).format(order['service_name'], order['flag'], order['country_name'], order['phone'])
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            return

        if not services:
            await update.message.reply_text("❌ Bortomane kono service add kora nei.")
            return

        sorted_services = sorted(services.items(), key=lambda x: get_discounted_price(x[1]['custom_price'], user['rank']))

        keyboard = []
        for key, s_data in sorted_services:
            final_price = get_discounted_price(s_data['custom_price'], user['rank'])
            btn_text = "{} {} - {} (${:.3f})".format(s_data['flag'], s_data['country_name'], s_data['service_name'], final_price)
            keyboard.append([InlineKeyboardButton(btn_text, callback_data="buynum_" + str(key))])

        keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="nav_back_main")])

        msg_title = "🛒 **Service list (Filtered & Price for Rank: {}):**".format(user['rank'])
        await update.message.reply_text(msg_title, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# ----------------- ADD SERVICE -----------------

async def admin_add_service_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        [InlineKeyboardButton("✈️ Telegram (< $0.40)", callback_data="addcat_tg"), InlineKeyboardButton("💬 WhatsApp (< $0.25)", callback_data="addcat_wa")],
        [InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="nav_back_admin")]
    ]
    await update.message.reply_text("📂 **Kon category-r service add korte chan select korun:**", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_category_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "nav_back_main":
        await query.message.delete()
        await start(update, context)
        return

    if data == "nav_back_admin":
        await query.edit_message_text("👑 **Admin Panel**")
        return

    if data.startswith("addcat_"):
        code = data.replace("addcat_", "")
        service_name = "Telegram" if code == "tg" else "WhatsApp"
        max_limit = MAX_COST_LIMITS.get(code, 1.0)

        params = {"api_key": SMSBOWER_API_KEY, "action": "getPrices", "service": code}
        
        try:
            res = requests.get(SMSBOWER_URL, params=params, timeout=10).json()
            country_list = []

            for cid, cdata in res.items():
                if code in cdata:
                    cost = float(cdata[code].get("cost", 0))
                    count = int(cdata[code].get("count", 0))
                    
                    if cost <= max_limit and count > 0:
                        cinfo = get_country_info(cid)
                        country_list.append({
                            "cid": cid,
                            "name": cinfo['name'],
                            "flag": cinfo['flag'],
                            "cost": cost,
                            "count": count
                        })

            country_list = sorted(country_list, key=lambda x: x['cost'])

            keyboard = []
            for item in country_list:
                s_key = "{}_{}".format(code, item['cid'])
                status = "✅ Added" if s_key in services else "➕ Add"
                
                btn_text = "{} {} - {} (${}) [Stock: {}] [{}]".format(
                    item['flag'], item['name'], service_name, item['cost'], item['count'], status
                )
                cb_data = "save_s_{}_{}".format(s_key, item['cost'])
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=cb_data)])

            keyboard.append([InlineKeyboardButton("🔙 Back to Categories", callback_data="nav_back_addcat")])

            if not keyboard:
                await query.edit_message_text("❌ ${} er niche kono desh/stock pawa jayni.".format(max_limit))
                return

            await query.edit_message_text("🌐 **{} (${} er kom rate-er desh shob Flag soho):**".format(service_name, max_limit), reply_markup=InlineKeyboardMarkup(keyboard))

        except Exception as err:
            await query.edit_message_text("❌ API data fetch error: " + str(err))

    elif data == "nav_back_addcat":
        await admin_add_service_menu(update, context)

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
        cinfo = get_country_info(cid)
        service_name = "Telegram" if code == "tg" else "WhatsApp"

        selling_price = cost + 0.05
        max_limit = MAX_COST_LIMITS.get(code, cost + 0.20)

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

        msg = (
            "✅ **{} {} - {}** Add kora hoyeche!\n"
            "💵 Cost: ${:.3f} | Base Selling Price: ${:.3f} \vert{} Max Limit:${:.3f}"
        ).format(cinfo['flag'], cinfo['name'], service_name, cost, selling_price, max_limit)

        keyboard = [[InlineKeyboardButton("🔙 Back to Country List", callback_data="addcat_" + code)]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

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
            await query.edit_message_text("❌ Service pawa jayni.")
            return

        try:
            p_res = requests.get(SMSBOWER_URL, params={"api_key": SMSBOWER_API_KEY, "action": "getPrices", "service": s_data['service_code'], "country": s_data['country_id']}, timeout=5).json()
            current_api_cost = float(p_res.get(s_data['country_id'], {}).get(s_data['service_code'], {}).get("cost", 999))
            
            s_data['cost_price'] = current_api_cost
            s_data['custom_price'] = current_api_cost + 0.05

            if current_api_cost > s_data['max_price']:
                msg_limit = "⚠️ **Dam besi hobar karone block kora hoyeche!**\nAPI Cost: ${:.3f}, Max Allowed:${:.3f}".format(current_api_cost, s_data['max_price'])
                await query.edit_message_text(msg_limit, parse_mode="Markdown")
                return
        except Exception:
            pass

        price = get_discounted_price(s_data['custom_price'], user['rank'])

        if user['balance'] < price:
            msg_bal = "❌ Porjapto balance nei! Proyojon: ${:.3f}, ache:${:.2f}".format(price, user['balance'])
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
                    "💵 **Rate ({}):** ${:.3f}\n\n"
                    "⚠️ OTP na asha porjonto opekkha korun..."
                ).format(s_data['service_name'], s_data['flag'], s_data['country_name'], phone, user['rank'], price)
                await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            else:
                msg_err = "❌ Number pawa jayni (Stock Empty)। API: " + str(res)
                await query.edit_message_text(msg_err)
        except Exception as e:
            msg_ex = "❌ API error: " + str(e)
            await query.edit_message_text(msg_ex)

    elif data.startswith("chk_otp_"):
        order = active_orders.get(user_id)
        if not order:
            await query.edit_message_text("❌ Apnar kono sokriyo number nei.")
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
            await query.answer("⏳ Ekhono OTP aseni, abar chesta korun...", show_alert=True)
        else:
            status_text = "Status: " + str(res)
            await query.answer(status_text, show_alert=True)

    elif data.startswith("cancel_ord_"):
        order = active_orders.get(user_id)
        if order:
            try:
                requests.get(SMSBOWER_URL, params={"api_key": SMSBOWER_API_KEY, "action": "setStatus", "status": 8, "id": order['activation_id']}, timeout=5)
            except Exception:
                pass
            user['balance'] += order['price']
            del active_orders[user_id]
            await query.edit_message_text("✅ Order batil kora hoyeche ebang balance ferot deya hoyeche.")

# ----------------- MAIN RUNNER -----------------

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_category_select, pattern="^(addcat_|nav_back_)"))
    app.add_handler(CallbackQueryHandler(handle_save_service, pattern="^save_s_"))
    app.add_handler(CallbackQueryHandler(handle_buy_action, pattern="^(buynum_|chk_otp_|cancel_ord_)"))

    app.add_handler(MessageHandler(filters.Regex("^(💳 Account Balance|🛒 Buy Number|👤 Profile|💳 Deposit|⚙️ Admin Panel|🔙 Main Menu)$"), handle_user_menu))
    app.add_handler(MessageHandler(filters.Regex("^➕ Add Service$"), admin_add_service_menu))

    print("🤖 Bot is starting cleanly with dynamic prices & rank system...")
    app.run_polling(drop_pending_updates=True)
