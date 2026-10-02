import os
import telebot
from telebot import types

# Shudhu telegram token railway variable theke neoa hobe
TOKEN = os.environ.get('BOT_TOKEN')

# Apnar asol telegram id ekhane din
ADMIN_ID = 7388500439          
BINANCE_ID = "123456789"       # Apnar binance pay id ekhane din
ADMIN_USERNAME = "SAIM_X9"     # Apnar username
DOLAR_RATE = 119.0             # Bortoman dolar rate
import os
import telebot
from telebot import types

import os
import telebot
from telebot import types

TOKEN = os.environ.get('BOT_TOKEN')

ADMIN_ID = 7388500439          
BINANCE_ID = "123456789"       
ADMIN_USERNAME = "SAIM_X9"     
DOLAR_RATE = 119.0             

bot = telebot.TeleBot(TOKEN)

user_state = {}
bot_status = {"is_active": True}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_sell = types.KeyboardButton("💵 𝐒𝐄𝐋𝐋 𝐃𝐎𝐋𝐋𝐄𝐑")
    btn_support = types.KeyboardButton("📞 𝐒𝐔𝐏𝐏𝐎𝐑𝐓")
    btn_admin = types.KeyboardButton("👑 𝐀𝐃𝐌𝐈𝐍 𝐏𝐀𝐍𝐄𝐋")
    markup.add(btn_sell, btn_support, btn_admin)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not bot_status["is_active"] and message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ Dukkhito! Bortomane amader service somoyassho vabe bondho royeche.")
        return
    
    user_state.pop(message.from_user.id, None)
    welcome_text = (
        f"🌙 𝐀𝐒𝐒𝐀𝐋𝐀𝐌𝐔 𝐀𝐋𝐀𝐈𝐊𝐔𝐌\n"
        f"👤 𝐈'𝐌 𝐒𝐀𝐈𝐌\n"
        f"👑 𝐀𝐃𝐌𝐈𝐍 𝐎𝐅 𝐔𝐍𝐈𝐕𝐄𝐑𝐒𝐄 𝐄𝐗𝐂𝐇𝐀𝐍𝐆𝐄𝐑 ⚡\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌟 Welcome to Universe Exchanger Zone!\n"
        f"💱 Rate: 1 USD = {DOLAR_RATE} Taka\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👇 Apnar proyojonio option-ti niche select korun:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text

    if not bot_status["is_active"] and user_id != ADMIN_ID:
        bot.reply_to(message, "⚠️ Bot-ti bortomane offline royeche.")
        return

    if text == "💵 𝐒𝐄𝐋𝐋 𝐃𝐎𝐋𝐋𝐄𝐑":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Binance", callback_data="binance_sell_option"))
        
        msg = (
            f"🌙 𝐀𝐒𝐒𝐀𝐋𝐀𝐌𝐔 𝐀𝐋𝐀𝐈𝐊𝐔𝐌\n"
            f"👤 𝐈'𝐌 𝐒𝐀𝐈𝐌\n"
            f"👑 𝐀𝐃𝐌𝐈𝐍 𝐎𝐅 𝐔𝐍𝐈𝐕𝐄𝐑𝐒𝐄 𝐄𝐗𝐂𝐇𝐀𝐍𝐆𝐄𝐑 ⚡\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📈 Rate: {DOLAR_RATE} Taka / USD\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👇 Doya kore nicher button-e click korun:"
        )
        bot.send_message(user_id, msg, reply_markup=markup)

    elif text == "📞 𝐒𝐔𝐏𝐏𝐎𝐑𝐓":
        user_state.pop(user_id, None)
        support_msg = (
            f"🛠 𝐂𝐮𝐬𝐭𝐨𝐦𝐞𝐫 𝐒𝐮𝐩𝐩𝐨𝐫𝐭 & 𝐇𝐞𝐥𝐩 𝐃𝐞𝐬𝐤\n\n"
            f"Jekono proyojone amader official admin-er sathe jogajog korun:\n\n"
            f"👤 Admin Username: @{ADMIN_USERNAME}"
        )
        bot.send_message(user_id, support_msg, reply_markup=main_menu())

    elif text == "👑 𝐀𝐃𝐌𝐈𝐍 𝐏𝐀𝐍𝐄𝐋":
        if user_id != ADMIN_ID:
            bot.send_message(user_id, f"❌ Apnar ei panel babohar korar permission nei!\n\nTelegram User ID: {user_id}", reply_markup=main_menu())
            return
        
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("📢 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭", callback_data="admin_broadcast"),
            types.InlineKeyboardButton("💱 𝐑𝐚𝐭𝐞 𝐂𝐡𝐚𝐧𝐠𝐞", callback_data="admin_rate"),
            types.InlineKeyboardButton("🔄 𝐁𝐨𝐭 𝐎𝐧/𝐎𝐟𝐟", callback_data="admin_toggle")
        )
        bot.send_message(user_id, "👑 Admin Control Panel\n\nNicher option-gulo theke kaj select korun:", reply_markup=admin_markup)

    elif user_state.get(user_id, {}).get("step") == "waiting_broadcast":
        if user_id == ADMIN_ID:
            user_state.pop(user_id, None)
            bot.send_message(user_id, f"✅ Broadcast shofolvabe somponno hoyeche!\n\nBarta:\n{text}", reply_markup=main_menu())

    elif user_state.get(user_id, {}).get("step") == "waiting_amount":
        try:
            amount = float(text)
            total_taka = amount * DOLAR_RATE
            user_state[user_id]["amount"] = amount
            user_state[user_id]["total_taka"] = total_taka
            user_state[user_id]["step"] = "waiting_order_id"

            try:
                bot.delete_message(user_id, message.message_id)
            except Exception:
                pass

            binance_msg = (
                f"🌙 𝐀𝐒𝐒𝐀𝐋𝐀𝐌𝐔 𝐀𝐋𝐀𝐈𝐊𝐔𝐌\n"
                f"👤 𝐈'𝐌 𝐒𝐀𝐈𝐌\n"
                f"👑 𝐀𝐃𝐌𝐈𝐍 𝐎𝐅 𝐔𝐍𝐈𝐕𝐄𝐑𝐒𝐄 𝐄𝐗𝐂𝐇𝐀𝐍𝐆𝐄𝐑 ⚡\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ Sell Korchen: {amount} USD\n"
                f"💰 Apni Paben: {total_taka} Taka\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💎 PAYMENT NIRDESHIKA:\n"
                f"Nicher Binance Pay ID-te dollar send korun:\n\n"
                f"🆔 Binance Pay ID: `{BINANCE_ID}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📥 Dollar pathanor por Order ID (TXID) ti ekhane likhe pathan:"
            )
            bot.send_message(user_id, binance_msg, parse_mode="Markdown", reply_markup=main_menu())
        except ValueError:
            bot.send_message(user_id, "⚠️ Doya kore sothik songkha likhun (jemon: 10 ba 20)", reply_markup=main_menu())

    elif user_state.get(user_id, {}).get("step") == "waiting_order_id":
        user_state[user_id]["order_id"] = text
        user_state[user_id]["step"] = "waiting_screenshot"
        
        try:
            bot.delete_message(user_id, message.message_id)
        except Exception:
            pass

        bot.send_message(
            user_id, 
            "✅ Order ID grohon kora hoyeche!\n\n📸 Ekhon apnar Binance Payment-er screenshot chobi akare pathan:", 
            reply_markup=main_menu()
        )

    elif user_state.get(user_id, {}).get("step") == "waiting_bkash":
        user_state[user_id]["bkash_number"] = text
        data = user_state[user_id]
        user_state[user_id]["step"] = "completed"

        summary_msg = (
            f"🌙 𝐀𝐒𝐒𝐀𝐋𝐀𝐌𝐔 𝐀𝐋𝐀𝐈𝐊𝐔𝐌\n"
            f"👤 𝐈'𝐌 𝐒𝐀𝐈𝐌\n"
            f"👑 𝐀𝐃𝐌𝐈𝐍 𝐎𝐅 𝐔𝐍𝐈𝐕𝐄𝐑𝐒𝐄 𝐄𝐗𝐂𝐇𝐀𝐍𝐆𝐄𝐑 ⚡\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎉 𝐀𝐏𝐍𝐀𝐑 𝐎𝐑𝐃𝐄𝐑 𝐒𝐔𝐁𝐌𝐈𝐓 𝐇𝐎𝐘𝐄𝐂𝐇𝐄!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 Dollar: {data['amount']} USD\n"
            f"💰 Taka: {data['total_taka']} BDT\n"
            f"🆔 Order ID: {data['order_id']}\n"
            f"📱 bKash Number: {data['bkash_number']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏳ 15 min opekkha korun. Payment somponno hole SMS paben."
        )
        bot.send_message(user_id, summary_msg, reply_markup=main_menu())

        admin_notification = (
            f"🚨 NOTUN DOLLAR SELL ORDER ESECHE! 🚨\n\n"
            f"👤 User ID: {user_id}\n"
            f"💵 Dollar: {data['amount']} USD\n"
            f"💱 Taka: {data['total_taka']} BDT\n"
            f"🆔 Order ID: {data['order_id']}\n"
            f"📱 bKash: {data['bkash_number']}"
        )
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("✅ Approve", callback_data=f"app_{user_id}"),
            types.InlineKeyboardButton("❌ Cancel", callback_data=f"rej_{user_id}")
        )
        
        if data.get("photo_file_id"):
            bot.send_photo(ADMIN_ID, data["photo_file_id"], caption=admin_notification, reply_markup=admin_markup)
        else:
            bot.send_message(ADMIN_ID, admin_notification, reply_markup=admin_markup)

@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    user_id = message.from_user.id
    if user_state.get(user_id, {}).get("step") == "waiting_screenshot":
        user_state[user_id]["photo_file_id"] = message.photo[-1].file_id
        user_state[user_id]["step"] = "waiting_bkash"
        
        try:
            bot.delete_message(user_id, message.message_id)
        except Exception:
            pass
        
        bot.send_message(
            user_id, 
            "✅ Screenshot songrokkhon kora hoyeche!\n\n"
            "💳 Ekhon apnar je bkash number-e taka nite chan ta niche likhe pathan:",
            reply_markup=main_menu()
        )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global DOLAR_RATE
    user_id = call.from_user.id
    data = call.data

    if data == "binance_sell_option":
        bot.answer_callback_query(call.id)
        
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            print(e)
            
        user_state[user_id] = {"step": "waiting_amount"}
        
        bot.send_message(
            user_id, 
            "✏️ Apni koto dollar (USD) sell korte chan?\n"
            "Doya kore shudhu songkha-ti (jemon: 10 ba 50) niche likhe pathan:"
        )
        return

    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Ei kaj korar permission apnar nei!", show_alert=True)
        return

    if data.startswith("app_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "Order approve kora hoyeche!")
        bot.send_message(
            target_user, 
            "🎉 𝐀𝐒𝐒𝐀𝐋𝐀𝐌𝐔 𝐀𝐋𝐀𝐈𝐊𝐔𝐌\n"
            "👤 𝐈'𝐌 𝐒𝐀𝐈𝐌\n"
            "👑 𝐀𝐃𝐌𝐈𝐍 𝐎𝐅 𝐔𝐍𝐈𝐕𝐄𝐑𝐒𝐄 𝐄𝐗𝐂𝐇𝐀𝐍𝐆𝐄𝐑 ⚡\n\n"
            "✅ 𝐏𝐀𝐘𝐌𝐄𝐍𝐓 𝐒𝐔𝐂𝐂𝐄𝐒𝐒𝐅𝐔𝐋\n"
            "Requested funds have been successfully sent to your provided number.", 
            reply_markup=main_menu()
        )
        try:
            bot.edit_message_caption(caption=call.message.caption + "\n\n✅ STATUS: APPROVED & PAID", chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception:
            bot.edit_message_text(text=call.message.text + "\n\n✅ STATUS: APPROVED & PAID", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data.startswith("rej_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "Order reject kora hoyeche.")
        bot.send_message(
            target_user, 
            "⚠️ Sotorkobarta! Apnar order-ti reject kora hoyeche. Sothik tottho diye abar chesta korun.", 
            reply_markup=main_menu()
        )
        try:
            bot.edit_message_caption(caption=call.message.caption + "\n\n❌ STATUS: REJECTED", chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception:
            bot.edit_message_text(text=call.message.text + "\n\n❌ STATUS: REJECTED", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data == "admin_toggle":
        bot_status["is_active"] = not bot_status["is_active"]
        status_text = "Active" if bot_status["is_active"] else "Off"
        bot.answer_callback_query(call.id, f"Bot Status: {status_text}", show_alert=True)

    elif data == "admin_rate":
        bot.answer_callback_query(call.id, f"Bortoman Rate: {DOLAR_RATE} Taka", show_alert=True)

    elif data == "admin_broadcast":
        user_state[ADMIN_ID] = {"step": "waiting_broadcast"}
        bot.send_message(ADMIN_ID, "📢 Broadcast message-ti likhe pathan:")

if __name__ == "__main__":
    print("Bot is starting on Railway...")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
