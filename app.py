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

# CONVERSATION STATES
WAITING_DEPOSIT_AMOUNT = 1
WAITING_TRX_ID = 2
WAITING_SCREENSHOT = 3

WAITING_BAN_ID = 4
WAITING_UNBAN_ID = 5
WAITING_BROADCAST_MSG = 6
WAITING_PRICE_SERVICE_KEY = 7
WAITING_NEW_PRICE = 8

# ----------------- IN-MEMORY STORAGE -----------------
users = {}          # {user_id: {name, username, balance, total_otp, is_banned}}
active_orders = {}  # {user_id: {activation_id, phone, service_name, country_name, flag, price}}
deposits = {}       # {deposit_id: {user_id, amount, trx_id, photo_id, status}}
traffic_log = []    # [{timestamp, service_name, country_name}]

# ONLY THE REQUESTED SERVICE IS CONFIGURED HERE
PREDEFINED_SERVICES = {
    "wa_usa_cellular": {
        "service_code": "wa", 
        "country_id": "12", 
        "operator": "cellular", 
        "country_name": "USA Virtual (Cellular)", 
        "flag": "🇺🇸", 
        "max_price": 0.120, 
        "selling_price": 0.120
    }
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

def get_admin_keyboard():
    keyboard = [
        [KeyboardButton("👥 View All Users"), KeyboardButton("💰 Set Service Price")],
        [KeyboardButton("📊 Live Traffic"), KeyboardButton("📢 Broadcast")],
        [KeyboardButton("🚫 Ban User"), KeyboardButton("✅ Unban User")],
        [KeyboardButton("🔙 Main Menu")]
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
        await update.message.reply_text("🚫 Apnake ban kora hoyeche.")
        return

    is_admin = (user_id == ADMIN_ID)
    msg = f"👋 **Hello {name}!**\n\nSwagotom amader SMS Service Bote."
    await update.message.reply_text(msg, reply_markup=get_main_keyboard(is_admin=is_admin), parse_mode="Markdown")

# ----------------- USER & ADMIN MENU HANDLERS -----------------

async def handle_user_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    name = update.effective_user.first_name
    username = update.effective_user.username
    user = get_user_data(user_id, name, username)

    if user["is_banned"]:
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

            total_user_bal = sum(u["balance"] for u in users.values())
            msg = (
                f"💳 **Admin Account Balance & Info:**\n\n"
                f"🌐 **SMS Bower API Balance:** ${sms_bal}\n"
                f"👥 **Total Bot Users:** {len(users)}\n"
                f"💰 **Total User Balances:** ${total_user_bal:.2f}"
            )
        else:
            msg = f"💳 **Apnar bortoman balance:** ${user['balance']:.2f}"
        
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "👤 Profile":
        msg = (
            f"👤 **User Profile**\n\n"
            f"🆔 ID: `{user_id}`\n"
            f"👤 Name: {user['name']}\n"
            f"💰 Balance: **${user['balance']:.2f}**\n"
            f"📩 Total OTP Received: **{user['total_otp']}**"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "🛒 Buy Number":
        if user_id in active_orders:
            order = active_orders[user_id]
            keyboard = [
                [InlineKeyboardButton("🔄 Check OTP", callback_data=f"chk_otp_{user_id}")],
                [InlineKeyboardButton("❌ Cancel Order", callback_data=f"cancel_ord_{user_id}")]
            ]
            msg = (
                f"📌 **Apnar ekti number active ache!**\n\n"
                f"🔹 Service: **{order['service_name']}**\n"
                f"{order['flag']} Country: **{order['country_name']}**\n"
                f"📞 Number: `{order['phone']}`"
            )
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            return

        # Direct show the available WhatsApp service list
        keyboard = []
        for s_key, s_data in PREDEFINED_SERVICES.items():
            btn_text = f"{s_data['flag']} {s_data['country_name']} - ${s_data['selling_price']:.3f}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"buynum_{s_key}")])

        keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="nav_back_main")])
        await update.message.reply_text("📂 **Available Services List:**", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "⚙️ Admin Panel" and user_id == ADMIN_ID:
        await update.message.reply_text("👑 **Admin Panele Swagotom!**", reply_markup=get_admin_keyboard(), parse_mode="Markdown")

    elif text == "👥 View All Users" and user_id == ADMIN_ID:
        if not users:
            await update.message.reply_text("❌ Kono user nei.")
            return
        
        msg = "👥 **Total Users List:**\n\n"
        for uid, udata in users.items():
            status = "🚫 Banned" if udata['is_banned'] else "✅ Active"
            msg += f"• `{uid}` | {udata['name']} | Bal: ${udata['balance']:.2f} | [{status}]\n"
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "📊 Live Traffic" and user_id == ADMIN_ID:
        if not traffic_log:
            await update.message.reply_text("📊 Kono live traffic log nei.")
            return
        
        msg = "📊 **Recent OTP Traffic Log:**\n\n"
        for t in traffic_log[-10:]:
            time_str = t['timestamp'].strftime("%H:%M:%S")
            msg += f"• [{time_str}] {t['service_name']} - {t['country_name']}\n"
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "🔙 Main Menu":
        await start(update, context)

# ----------------- BUY NUMBER FLOW -----------------

async def handle_category_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "nav_back_main":
        await query.message.delete()
        await start(update, context)
        return

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

        real_price = s_data['selling_price']
        try:
            p_params = {
                "api_key": SMSBOWER_API_KEY,
                "action": "getPricesV3",
                "service": s_data['service_code'],
                "country": s_data['country_id']
            }
            p_res = requests.get(SMSBOWER_URL, params=p_params, timeout=5).json()
            real_price = float(p_res.get(s_data['country_id'], {}).get(s_data['service_code'], {}).get("cost", s_data['selling_price']))
        except Exception:
            pass

        if real_price > s_data['max_price']:
            err_msg = (
                f"⚠️ **Actual Rate Check Failed!**\n"
                f"Required Max Limit: **${s_data['max_price']:.3f}**\n"
                f"Current Actual Market Price: **${real_price:.3f}**\n\n"
                f"❌ দাম বেশি থাকায় (Actual Rate match na koray) নাম্বার কেনা সম্ভব হলো না।"
            )
            await query.edit_message_text(err_msg, parse_mode="Markdown")
            return

        if user['balance'] < real_price:
            msg_bal = f"❌ Porjapto balance nei! Proyojon: ${real_price:.3f}, Apnar Balance:${user['balance']:.2f}"
            await query.edit_message_text(msg_bal)
            return

        params = {
            "api_key": SMSBOWER_API_KEY,
            "action": "getNumber",
            "service": s_data['service_code'],
            "country": s_data['country_id']
        }
        
        if "operator" in s_data:
            params["operator"] = s_data["operator"]

        try:
            res = requests.get(SMSBOWER_URL, params=params, timeout=10).text
            if "ACCESS_NUMBER" in res:
                parts = res.split(":")
                act_id = parts[1]
                phone = parts[2]

                user['balance'] -= real_price
                service_name = "WhatsApp"

                active_orders[user_id] = {
                    "activation_id": act_id,
                    "phone": phone,
                    "service_name": service_name,
                    "country_name": s_data['country_name'],
                    "flag": s_data['flag'],
                    "price": real_price
                }

                keyboard = [
                    [InlineKeyboardButton("🔄 Check OTP", callback_data=f"chk_otp_{user_id}")],
                    [InlineKeyboardButton("❌ Cancel Order", callback_data=f"cancel_ord_{user_id}")]
                ]

                msg = (
                    f"🏷 **Service:** {service_name}\n"
                    f"{s_data['flag']} **Country:** {s_data['country_name']}\n"
                    f"📞 **Number:** `{phone}`\n"
                    f"💵 **Rate Deducted:** ${real_price:.3f}\n\n"
                    f"⚠️ OTP na asha porjonto opekkha korun..."
                )
                await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            else:
                msg_err = f"❌ Stock Empty ba Service Unavailable. API Response: {res}"
                await query.edit_message_text(msg_err)
        except Exception as e:
            msg_ex = f"❌ API error: {str(e)}"
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
                f"🎉 **OTP Received!**\n\n"
                f"🏷 Service: {order['service_name']}\n"
                f"📞 Number: `{order['phone']}`\n"
                f"💬 **OTP:** `{otp_code}`"
            )
            del active_orders[user_id]
            await query.edit_message_text(msg, parse_mode="Markdown")
        elif "STATUS_WAIT_CODE" in res:
            await query.answer("⏳ Ekhono OTP aseni, abar chesta korun...", show_alert=True)
        else:
            await query.answer(f"Status: {res}", show_alert=True)

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

# ----------------- ADMIN PRICE SETTING CONVERSATION -----------------

async def admin_set_price_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    keyboard = []
    for s_key, s_data in PREDEFINED_SERVICES.items():
        btn_text = f"{s_data['flag']} {s_data['country_name']} (Cur: ${s_data['selling_price']})"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"setpr_{s_key}")])

    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="admin_cancel")])
    await update.message.reply_text("💰 **Kon service-er custom price set korte chan select korun:**", reply_markup=InlineKeyboardMarkup(keyboard))
    return WAITING_PRICE_SERVICE_KEY

async def admin_price_service_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "admin_cancel":
        await query.edit_message_text("❌ Cancelled.")
        return ConversationHandler.END

    s_key = query.data.replace("setpr_", "")
    context.user_data['selected_service_key'] = s_key
    s_data = PREDEFINED_SERVICES[s_key]

    msg = f"📝 **{s_data['flag']} {s_data['country_name']}** -er jonno new selling price ($) type korun:"
    await query.edit_message_text(msg, parse_mode="Markdown")
    return WAITING_NEW_PRICE

async def admin_save_new_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        new_price = float(update.message.text.strip())
        s_key = context.user_data['selected_service_key']
        
        PREDEFINED_SERVICES[s_key]['selling_price'] = new_price
        PREDEFINED_SERVICES[s_key]['max_price'] = new_price
        s_data = PREDEFINED_SERVICES[s_key]

        msg = f"✅ Price Updated!\n\n{s_data['flag']} **{s_data['country_name']}** Custom Price set to: **${new_price:.3f}**"
        await update.message.reply_text(msg, parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ Shothik songkha likhun. Example: 0.12")
        return WAITING_NEW_PRICE

    return ConversationHandler.END

# ----------------- ADMIN BAN / UNBAN / BROADCAST -----------------

async def admin_ban_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return ConversationHandler.END
    await update.message.reply_text("🚫 Ban korar jonno User ID type korun:")
    return WAITING_BAN_ID

async def admin_ban_submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        target_id = int(update.message.text.strip())
        if target_id in users:
            users[target_id]['is_banned'] = True
            await update.message.reply_text(f"✅ User `{target_id}` ban kora hoyeche.", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ User ID pawa jayni.")
    except ValueError:
        await update.message.reply_text("❌ Invalid ID format.")
    return ConversationHandler.END

async def admin_unban_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return ConversationHandler.END
    await update.message.reply_text("✅ Unban korar jonno User ID type korun:")
    return WAITING_UNBAN_ID

async def admin_unban_submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        target_id = int(update.message.text.strip())
        if target_id in users:
            users[target_id]['is_banned'] = False
            await update.message.reply_text(f"✅ User `{target_id}` unban kora hoyeche.", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ User ID pawa jayni.")
    except ValueError:
        await update.message.reply_text("❌ Invalid ID format.")
    return ConversationHandler.END

async def admin_broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return ConversationHandler.END
    await update.message.reply_text("📢 Sob user-er kache jabe emon broadcast text message-ti type korun:")
    return WAITING_BROADCAST_MSG

async def admin_broadcast_submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    count = 0
    for uid in users.keys():
        try:
            b_msg = f"📢 **Notification:**\n\n{msg}"
            await context.bot.send_message(chat_id=uid, text=b_msg, parse_mode="Markdown")
            count += 1
        except Exception:
            pass
    await update.message.reply_text(f"✅ Broadcast success! `{count}` jon user message peyeche.", parse_mode="Markdown")
    return ConversationHandler.END

# ----------------- BINANCE DEPOSIT FLOW -----------------

async def deposit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🟡 Binance Pay ($1.00 Min)", callback_data="dep_binance")],
        [InlineKeyboardButton("🔙 Cancel", callback_data="dep_cancel")]
    ]
    await update.message.reply_text("💳 **Kon payment method diye deposit korte chan?**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return WAITING_DEPOSIT_AMOUNT

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
            f"🟡 **Binance Payment Details:**\n\n"
            f"🆔 **Binance Pay ID:** `{BINANCE_PAY_ID}`\n"
            f"💵 **Amount to Send:** **${amount:.2f}**\n\n"
            f"⚠️ Send korar por apnar Binance **Order ID / TRX ID**-ti type kore pathan:"
        )

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

    await update.message.reply_text("✅ **Apnar deposit request admin-er kache pathano hoyeche!**\nAdmin verify kore approve korle balance add hoye jabe.")

    if ADMIN_ID != 0:
        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"depapp_{dep_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"deprej_{dep_id}")
            ]
        ]
        admin_msg = (
            f"📥 **New Deposit Request!**\n\n"
            f"👤 User: **{name}** (`{user_id}`)\n"
            f"💵 Amount: **${amount:.2f}**\n"
            f"🔖 TRX/Order ID: `{trx_id}`"
        )

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

# ----------------- ADMIN APPROVAL HANDLER -----------------

async def handle_admin_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("depapp_") or data.startswith("deprej_"):
        dep_id = data.split("_")[1]
        dep_info = deposits.get(dep_id)

        if not dep_info:
            await query.edit_message_caption("❌ Deposit request pawa jayni.")
            return

        target_user = users.get(dep_info['user_id'])

        if data.startswith("depapp_"):
            dep_info['status'] = "approved"
            if target_user:
                target_user['balance'] += dep_info['amount']

            try:
                msg_u = f"🎉 **Apnar deposit approve hoyeche!**\n💵 Added: **${dep_info['amount']:.2f}**"
                await context.bot.send_message(chat_id=dep_info['user_id'], text=msg_u, parse_mode="Markdown")
            except Exception:
                pass

            await query.edit_message_caption(caption=f"✅ **Deposit Request Approved!**\nAmount: ${dep_info['amount']:.2f}")

        elif data.startswith("deprej_"):
            dep_info['status'] = "rejected"
            try:
                msg_u = "❌ **Apnar deposit request-ti reject kora hoyeche.**"
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

    # Admin Set Price Conversation Handler
    price_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💰 Set Service Price$"), admin_set_price_start)],
        states={
            WAITING_PRICE_SERVICE_KEY: [CallbackQueryHandler(admin_price_service_selected, pattern="^(setpr_|admin_cancel)")],
            WAITING_NEW_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_save_new_price)]
        },
        fallbacks=[CommandHandler("start", start)]
    )

    # Admin Ban Conversation Handler
    ban_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🚫 Ban User$"), admin_ban_start)],
        states={WAITING_BAN_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_ban_submit)]},
        fallbacks=[CommandHandler("start", start)]
    )

    # Admin Unban Conversation Handler
    unban_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^✅ Unban User$"), admin_unban_start)],
        states={WAITING_UNBAN_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_unban_submit)]},
        fallbacks=[CommandHandler("start", start)]
    )

    # Admin Broadcast Conversation Handler
    broadcast_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📢 Broadcast$"), admin_broadcast_start)],
        states={WAITING_BROADCAST_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_broadcast_submit)]},
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(deposit_conv)
    app.add_handler(price_conv)
    app.add_handler(ban_conv)
    app.add_handler(unban_conv)
    app.add_handler(broadcast_conv)

    app.add_handler(CallbackQueryHandler(handle_category_select, pattern="^nav_back_"))
    app.add_handler(CallbackQueryHandler(handle_buy_action, pattern="^(buynum_|chk_otp_|cancel_ord_)"))
    app.add_handler(CallbackQueryHandler(handle_admin_approval, pattern="^(depapp_|deprej_)"))

    app.add_handler(MessageHandler(filters.Regex("^(💳 Account Balance|🛒 Buy Number|👤 Profile|⚙️ Admin Panel|👥 View All Users|📊 Live Traffic|🔙 Main Menu)$"), handle_user_menu))

    print("🤖 Bot running with only USA Virtual (Cellular) service (Country ID: 12, Operator: cellular, Price: 0.12)...")
    app.run_polling(drop_pending_updates=True)
