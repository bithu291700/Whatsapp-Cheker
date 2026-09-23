import os
import sys
import logging
import requests
from datetime import datetime
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

# CONVERSATION STATES FOR DEPOSIT
WAITING_DEPOSIT_AMOUNT = 1
WAITING_TRX_ID = 2
WAITING_SCREENSHOT = 3

# ----------------- IN-MEMORY STORAGE -----------------
users = {}          # {user_id: {name, username, balance, total_otp, is_banned}}
active_orders = {}  # {user_id: {activation_id, phone, service_name, country_name, flag, price}}
deposits = {}       # {deposit_id: {user_id, amount, trx_id, photo_id, status}}

# FIXED ALLOWED SERVICES (WhatsApp & Telegram)
PREDEFINED_SERVICES = {
    # --- WHATSAPP SERVICES ---
    "wa_usa_1": {"service_code": "wa", "country_id": "187", "country_name": "USA Virtual (Tier 1)", "flag": "🇺🇸", "max_price": 0.12, "selling_price": 0.12},
    "wa_usa_2": {"service_code": "wa", "country_id": "187", "country_name": "USA Virtual (Tier 2)", "flag": "🇺🇸", "max_price": 0.134, "selling_price": 0.134},
    "wa_iraq_1": {"service_code": "wa", "country_id": "185", "country_name": "Iraq (Tier 1)", "flag": "🇮🇶", "max_price": 0.151, "selling_price": 0.151},
    "wa_iraq_2": {"service_code": "wa", "country_id": "185", "country_name": "Iraq (Tier 2)", "flag": "🇮🇶", "max_price": 0.163, "selling_price": 0.163},
    "wa_ph": {"service_code": "wa", "country_id": "4", "country_name": "Philippines", "flag": "🇵🇭", "max_price": 0.144, "selling_price": 0.144},
    "wa_ua": {"service_code": "wa", "country_id": "1", "country_name": "Ukraine", "flag": "🇺🇦", "max_price": 0.039, "selling_price": 0.039},
    "wa_gh": {"service_code": "wa", "country_id": "38", "country_name": "Ghana", "flag": "🇬🇭", "max_price": 0.067, "selling_price": 0.067},
    "wa_af": {"service_code": "wa", "country_id": "179", "country_name": "Afghanistan", "flag": "🇦🇫", "max_price": 0.119, "selling_price": 0.119},

    # --- TELEGRAM SERVICES ---
    "tg_usa": {"service_code": "tg", "country_id": "187", "country_name": "USA Virtual", "flag": "🇺🇸", "max_price": 0.20, "selling_price": 0.20},
    "tg_am": {"service_code": "tg", "country_id": "148", "country_name": "Armenia", "flag": "🇦🇲", "max_price": 0.354, "selling_price": 0.354},
    "tg_cl": {"service_code": "tg", "country_id": "151", "country_name": "Chile", "flag": "🇨🇱", "max_price": 0.108, "selling_price": 0.108},
    "tg_ca": {"service_code": "tg", "country_id": "36", "country_name": "Canada", "flag": "🇨🇦", "max_price": 0.132, "selling_price": 0.132},
    "tg_iq": {"service_code": "tg", "country_id": "185", "country_name": "Iraq", "flag": "🇮🇶", "max_price": 0.354, "selling_price": 0.354}
}

# ----------------- KEYBOARDS -----------------

def get_main_keyboard(is_admin=False):
    keyboard = [
        [KeyboardButton("💳 Account Balance"), KeyboardButton("🛒 Buy Number")],
        [KeyboardButton("👤 Profile"), KeyboardButton("💳 Deposit")]
    ]
    if is_admin:
        keyboard.append([KeyboardButton("⚙️ Admin Panel")])
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
        await update.message.reply_text("🚫 Apnake bote ban kora hoyeche.")
        return

    is_admin = (user_id == ADMIN_ID)
    msg = "👋 **Hello {}!**\n\nSwagotom amader SMS Service Bote.".format(name)
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
            "💰 Balance: **${:.2f}**\n"
            "📩 Total OTP Received: **{}**"
        ).format(user_id, user['name'], user['balance'], user['total_otp'])
        await update.message.reply_text(msg, parse_mode="Markdown")

    # 3. BUY NUMBER MENU
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

        keyboard = [
            [InlineKeyboardButton("💬 WhatsApp Services", callback_data="cat_wa")],
            [InlineKeyboardButton("✈️ Telegram Services", callback_data="cat_tg")],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="nav_back_main")]
        ]
        await update.message.reply_text("📂 **Kon service-er number kinte chan select korun:**", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "🔙 Main Menu":
        await start(update, context)

# ----------------- BUY NUMBER & CATEGORY FLOW -----------------

async def handle_category_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "nav_back_main":
        await query.message.delete()
        await start(update, context)
        return

    if data in ["cat_wa", "cat_tg"]:
        code = "wa" if data == "cat_wa" else "tg"
        service_label = "WhatsApp" if code == "wa" else "Telegram"

        keyboard = []
        for s_key, s_data in PREDEFINED_SERVICES.items():
            if s_data['service_code'] == code:
                btn_text = "{} {} - ${:.3f}".format(s_data['flag'], s_data['country_name'], s_data['selling_price'])
                keyboard.append([InlineKeyboardButton(btn_text, callback_data="buynum_" + str(s_key))])

        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="nav_back_buymenu")])
        
        msg_title = "🌐 **{} Services List (Fixed Lowest Rates):**".format(service_label)
        await query.edit_message_text(msg_title, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "nav_back_buymenu":
        keyboard = [
            [InlineKeyboardButton("💬 WhatsApp Services", callback_data="cat_wa")],
            [InlineKeyboardButton("✈️ Telegram Services", callback_data="cat_tg")],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="nav_back_main")]
        ]
        await query.edit_message_text("📂 **Kon service-er number kinte chan select korun:**", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_buy_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    user = get_user_data(user_id, query.from_user.first_name, query.from_user.username)

    if data.startswith("buynum_"):
        s_key = data.replace("buynum_", "")
        s_data = PREDEFINED_SERVICES.get(s_key)

        if not s_data:
            await query.edit_message_text("❌ Service pawa jayni.")
            return

        # Realtime Price & Limit Safety Check from API
        try:
            p_res = requests.get(SMSBOWER_URL, params={"api_key": SMSBOWER_API_KEY, "action": "getPrices", "service": s_data['service_code'], "country": s_data['country_id']}, timeout=5).json()
            current_api_cost = float(p_res.get(s_data['country_id'], {}).get(s_data['service_code'], {}).get("cost", 999))
            
            if current_api_cost > s_data['max_price']:
                msg_limit = "⚠️ **Dam besi hobar karone block kora hoyeche!**\nAPI Cost: ${:.3f}, Max Allowed:${:.3f}".format(current_api_cost, s_data['max_price'])
                await query.edit_message_text(msg_limit, parse_mode="Markdown")
                return
        except Exception:
            pass

        price = s_data['selling_price']

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

                service_name = "WhatsApp" if s_data['service_code'] == "wa" else "Telegram"

                active_orders[user_id] = {
                    "activation_id": act_id,
                    "phone": phone,
                    "service_name": service_name,
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
                    "💵 **Rate:** ${:.3f}\n\n"
                    "⚠️ OTP na asha porjonto opekkha korun..."
                ).format(service_name, s_data['flag'], s_data['country_name'], phone, price)
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

# ----------------- BINANCE DEPOSIT FLOW -----------------

async def deposit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🟡 Binance Pay ($1.00 Min)", callback_data="dep_binance")],
        [InlineKeyboardButton("🔙 Cancel", callback_data="dep_cancel")]
    ]
    await update.message.reply_text("💳 **Kon payment method diye deposit korte chan?**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def deposit_method_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "dep_cancel":
        await query.edit_message_text("❌ Deposit batil kora hoyeche.")
        return ConversationHandler.END

    if query.data == "dep_binance":
        await query.edit_message_text("💵 **Koto dollar deposit korte chan likhun (Minimum $1.00):**")
        return WAITING_DEPOSIT_AMOUNT

async def deposit_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text.strip())
        if amount < 1.0:
            await update.message.reply_text("❌ Minimum deposit amount $1.00! Abar amount likhun:")
            return WAITING_DEPOSIT_AMOUNT

        context.user_data['deposit_amount'] = amount

        msg = (
            "🟡 **Binance Payment Details:**\n\n"
            "🆔 **Binance Pay ID:** `{}`\n"
            "💵 **Amount to Send:** **${:.2f}**\n\n"
            "⚠️ Send korar por apnar Binance **Order ID / TRX ID**-ti type kore pathan:"
        ).format(BINANCE_PAY_ID, amount)

        await update.message.reply_text(msg, parse_mode="Markdown")
        return WAITING_TRX_ID

    except ValueError:
        await update.message.reply_text("❌ Shothik songkha (number) likhun. (Example: 1.5):")
        return WAITING_DEPOSIT_AMOUNT

async def deposit_trx_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['trx_id'] = update.message.text.strip()
    await update.message.reply_text("📸 **Abar apnar Payment Screenshot (Photo)-ti pathan:**")
    return WAITING_SCREENSHOT

async def deposit_screenshot_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.effective_user.first_name
    photo_id = update.message.photo[-1].file_id

    amount = context.user_data['deposit_amount']
    trx_id = context.user_data['trx_id']

    dep_id = str(int(datetime.now().timestamp()))
    deposits[dep_id] = {
        "user_id": user_id,
        "amount": amount,
        "trx_id": trx_id,
        "photo_id": photo_id,
        "status": "pending"
    }

    # User Confirmation
    await update.message.reply_text("✅ **Apnar deposit request admin-er kache pathano hoyeche!**\nAdmin verify kore approve korle balance add hoye jabe.")

    # Send Notification to Admin
    if ADMIN_ID != 0:
        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data="depapp_{}".format(dep_id)),
                InlineKeyboardButton("❌ Reject", callback_data="deprej_{}".format(dep_id))
            ]
        ]
        admin_msg = (
            "📥 **New Deposit Request!**\n\n"
            "👤 User: **{}** (`{}`)\n"
            "💵 Amount: **${:.2f}**\n"
            "🔖 TRX/Order ID: `{}`"
        ).format(name, user_id, amount, trx_id)

        try:
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo_id,
                caption=admin_msg,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        except Exception as e:
            print("Admin notification error:", e)

    return ConversationHandler.END

# ----------------- ADMIN DEPOSIT APPROVAL HANDLER -----------------

async def handle_admin_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("depapp_") or data.startswith("deprej_"):
        dep_id = data.split("_")[1]
        dep_info = deposits.get(dep_id)

        if not dep_info:
            await query.edit_message_caption("❌ Deposit request pawa jayni ba expired.")
            return

        target_user = users.get(dep_info['user_id'])

        if data.startswith("depapp_"):
            dep_info['status'] = "approved"
            if target_user:
                target_user['balance'] += dep_info['amount']

            # Notify User
            try:
                msg_u = "🎉 **Apnar deposit approve hoyeche!**\n💵 Added: **${:.2f}**".format(dep_info['amount'])
                await context.bot.send_message(chat_id=dep_info['user_id'], text=msg_u, parse_mode="Markdown")
            except Exception:
                pass

            await query.edit_message_caption(caption="✅ **Deposit Request Approved!**\nAmount: ${:.2f}".format(dep_info['amount']))

        elif data.startswith("deprej_"):
            dep_info['status'] = "rejected"
            try:
                msg_u = "❌ **Apnar deposit request-ti reject kora hoyeche.**\nTRX ID Check korun ba support-e jogajog korun."
                await context.bot.send_message(chat_id=dep_info['user_id'], text=msg_u, parse_mode="Markdown")
            except Exception:
                pass

            await query.edit_message_caption(caption="❌ **Deposit Request Rejected!**")

# ----------------- MAIN RUNNER -----------------

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Deposit Conversation Handler
    deposit_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💳 Deposit$"), deposit_start)],
        states={
            WAITING_DEPOSIT_AMOUNT: [
                CallbackQueryHandler(deposit_method_select, pattern="^dep_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, deposit_amount_received)
            ],
            WAITING_TRX_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, deposit_trx_received)],
            WAITING_SCREENSHOT: [MessageHandler(filters.PHOTO, deposit_screenshot_received)]
        },
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(deposit_conv)

    app.add_handler(CallbackQueryHandler(handle_category_select, pattern="^(cat_|nav_back_)"))
    app.add_handler(CallbackQueryHandler(handle_buy_action, pattern="^(buynum_|chk_otp_|cancel_ord_)"))
    app.add_handler(CallbackQueryHandler(handle_admin_approval, pattern="^(depapp_|deprej_)"))

    app.add_handler(MessageHandler(filters.Regex("^(💳 Account Balance|🛒 Buy Number|👤 Profile|🔙 Main Menu)$"), handle_user_menu))

    print("🤖 Bot is running smoothly with clean syntax & deposit flow...")
    app.run_polling(drop_pending_updates=True)
