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
    btn_sell = types.KeyboardButton("💵 𝗦𝗘𝗟𝗟 𝗗𝗢𝗟𝗟𝗘𝗥")
    btn_support = types.KeyboardButton("📞 𝗦𝗨𝗣𝗣𝗢𝗥𝗧")
    btn_admin = types.KeyboardButton("👑 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟")
    markup.add(btn_sell, btn_support, btn_admin)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not bot_status["is_active"] and message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ 𝗗𝗨𝗞𝗞𝗛𝗜𝗧𝗢! 𝗕𝗢𝗥𝗧𝗢𝗠𝗔𝗡𝗘 𝗔𝗠𝗔𝗗𝗘𝗥 𝗦𝗘𝗥𝗩𝗜𝗖𝗘 𝗕𝗢𝗡𝗗𝗛𝗢 𝗥𝗢𝗬𝗘𝗖𝗛𝗘.")
        return
    
    user_state.pop(message.from_user.id, None)
    welcome_text = (
        f"🌙 𝗔𝗦𝗦𝗔𝗟𝗔𝗠𝗨 𝗔𝗟𝗔𝗜𝗞𝗨𝗠\n"
        f"👤 𝗜'𝗠 𝗦𝗔𝗜𝗠\n"
        f"👑 𝗔𝗗𝗠𝗜𝗡 𝗢𝗙 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧 ⚡\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌟 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧 𝗭𝗢𝗡𝗘!\n"
        f"💱 𝗥𝗔𝗧𝗘: 1 𝗨𝗦𝗗 = {DOLAR_RATE} 𝗧𝗔𝗞𝗔\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👇 𝗔𝗣𝗡𝗔𝗥 𝗣𝗥𝗢𝗬𝗢𝗝𝗢𝗡𝗜𝗢 𝗢𝗣𝗧𝗜𝗢𝗡-𝗧𝗜 𝗡𝗜𝗖𝗛𝗘 𝗦𝗘𝗟𝗘𝗖𝗧 𝗞𝗢𝗥𝗨𝗡:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text

    if not bot_status["is_active"] and user_id != ADMIN_ID:
        bot.reply_to(message, "⚠️ 𝗕𝗢𝗧-𝗧𝗜 𝗕𝗢𝗥𝗧𝗢𝗠𝗔𝗡𝗘 𝗢𝗙𝗙𝗟𝗜𝗡𝗘 𝗥𝗢𝗬𝗘𝗖𝗛𝗘.")
        return

    if text == "💵 𝗦𝗘𝗟𝗟 𝗗𝗢𝗟𝗟𝗘𝗥":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("𝗕𝗜𝗡𝗔𝗡𝗖𝗘", callback_data="binance_sell_option"))
        
        msg = (
            f"🌙 𝗔𝗦𝗦𝗔𝗟𝗔𝗠𝗨 𝗔𝗟𝗔𝗜𝗞𝗨𝗠\n"
            f"👤 𝗜'𝗠 𝗦𝗔𝗜𝗠\n"
            f"👑 𝗔𝗗𝗠𝗜𝗡 𝗢𝗙 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧 ⚡\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📈 𝗥𝗔𝗧𝗘: {DOLAR_RATE} 𝗧𝗔𝗞𝗔 / 𝗨𝗦𝗗\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👇 𝗗𝗢𝗬𝗔 𝗞𝗢𝗥𝗘 𝗡𝗜𝗖𝗛𝗘𝗥 𝗕𝗨𝗧𝗧𝗢𝗡-𝗘 𝗖𝗟𝗜𝗖𝗞 𝗞𝗢𝗥𝗨𝗡:"
        )
        bot.send_message(user_id, msg, reply_markup=markup)

    elif text == "📞 𝗦𝗨𝗣𝗣𝗢𝗥𝗧":
        user_state.pop(user_id, None)
        support_msg = (
            f"🛠 𝗖𝗨𝗦𝗧𝗢𝗠𝗘𝗥 𝗦𝗨𝗣𝗣𝗢𝗥𝗧 & 𝗛𝗘𝗟𝗣 𝗗𝗘𝗦𝗞\n\n"
            f"𝗝𝗘𝗞𝗢𝗡𝗢 𝗣𝗥𝗢𝗬𝗢𝗝𝗢𝗡𝗘 𝗔𝗠𝗔𝗗𝗘𝗥 𝗢𝗙𝗙𝗜𝗖𝗜𝗔𝗟 𝗔𝗗𝗠𝗜𝗡-𝗘𝗥 𝗦𝗔𝗧𝗛𝗘 𝗝𝗢𝗚𝗔𝗝𝗢𝗚 𝗞𝗢𝗥𝗨𝗡:\n\n"
            f"👤 𝗔𝗗𝗠𝗜𝗡 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘: @{ADMIN_USERNAME}"
        )
        bot.send_message(user_id, support_msg, reply_markup=main_menu())

    elif text == "👑 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟":
        if user_id != ADMIN_ID:
            bot.send_message(user_id, f"❌ 𝗔𝗣𝗡𝗔𝗥 𝗘𝗜 𝗣𝗔𝗡𝗘𝗟 𝗕𝗔𝗕𝗢𝗛𝗔𝗥 𝗞𝗢𝗥𝗔𝗥 𝗣𝗘𝗥𝗠𝗜𝗦𝗦𝗜𝗢𝗡 𝗡𝗘𝗜!\n\n𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗠 𝗨𝗦𝗘𝗥 𝗜𝗗: {user_id}", reply_markup=main_menu())
            return
        
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("📢 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧", callback_data="admin_broadcast"),
            types.InlineKeyboardButton("💱 𝗥𝗔𝗧𝗘 𝗖𝗛𝗔𝗡𝗚𝗘", callback_data="admin_rate"),
            types.InlineKeyboardButton("🔄 𝗕𝗢𝗧 𝗢𝗡/𝗢𝗙𝗙", callback_data="admin_toggle")
        )
        bot.send_message(user_id, "👑 𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗡𝗧𝗥𝗢𝗟 𝗣𝗔𝗡𝗘𝗟\n\n𝗡𝗜𝗖𝗛𝗘𝗥 𝗢𝗣𝗧𝗜𝗢𝗡-𝗚𝗨𝗟𝗢 𝗧𝗛𝗘𝗞𝗘 𝗞𝗔𝗝 𝗦𝗘𝗟𝗘𝗖𝗧 𝗞𝗢𝗥𝗨𝗡:", reply_markup=admin_markup)

    elif user_state.get(user_id, {}).get("step") == "waiting_broadcast":
        if user_id == ADMIN_ID:
            user_state.pop(user_id, None)
            bot.send_message(user_id, f"✅ 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗦𝗛𝗢𝗙𝗢𝗟𝗩𝗔𝗕𝗘 𝗦𝗢𝗠𝗣𝗢𝗡𝗡𝗢 𝗛𝗢𝗬𝗘𝗖𝗛𝗘!\n\n𝗕𝗔𝗥𝗧𝗔:\n{text}", reply_markup=main_menu())

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
                f"🌙 𝗔𝗦𝗦𝗔𝗟𝗔𝗠𝗨 𝗔𝗟𝗔𝗜𝗞𝗨𝗠\n"
                f"👤 𝗜'𝗠 𝗦𝗔𝗜𝗠\n"
                f"👑 𝗔𝗗𝗠𝗜𝗡 𝗢𝗙 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧 ⚡\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ 𝗦𝗘𝗟𝗟 𝗞𝗢𝗥𝗖𝗛𝗘𝗡: {amount} 𝗨𝗦𝗗\n"
                f"💰 𝗔𝗣𝗡𝗜 𝗣𝗔𝗕𝗘𝗡: {total_taka} 𝗧𝗔𝗞𝗔\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💎 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗡𝗜𝗥𝗗𝗘𝗦𝗛𝗜𝗞𝗔:\n"
                f"𝗡𝗜𝗖𝗛𝗘𝗥 𝗕𝗜𝗡𝗔𝗡𝗖𝗘 𝗣𝗔𝗬 𝗜𝗗-𝗧𝗘 𝗗𝗢𝗟𝗟𝗔𝗥 𝗦𝗘𝗡𝗗 𝗞𝗢𝗥𝗨𝗡:\n\n"
                f"🆔 𝗕𝗜𝗡𝗔𝗡𝗖𝗘 𝗣𝗔𝗬 𝗜𝗗: `{BINANCE_ID}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📥 𝗗𝗢𝗟𝗟𝗔𝗥 𝗣𝗔𝗧𝗛𝗔𝗡𝗢𝗥 𝗣𝗢𝗥 𝗢𝗥𝗗𝗘𝗥 𝗜𝗗 (𝗧𝗫𝗜𝗗) 𝗧𝗜 𝗘𝗞𝗛𝗔𝗡𝗘 𝗟𝗜𝗞𝗛𝗘 𝗣𝗔𝗧𝗛𝗔𝗡:"
            )
            bot.send_message(user_id, binance_msg, parse_mode="Markdown", reply_markup=main_menu())
        except ValueError:
            bot.send_message(user_id, "⚠️ 𝗗𝗢𝗬𝗔 𝗞𝗢𝗥𝗘 𝗦𝗢𝗧𝗛𝗜𝗞 𝗦𝗢𝗡𝗚𝗞𝗛𝗔 𝗟𝗜𝗞𝗛𝗨𝗡 (𝗝𝗘𝗠𝗢𝗡: 10 𝗕𝗔 20)", reply_markup=main_menu())

    elif user_state.get(user_id, {}).get("step") == "waiting_order_id":
        user_state[user_id]["order_id"] = text
        user_state[user_id]["step"] = "waiting_screenshot"
        
        try:
            bot.delete_message(user_id, message.message_id)
        except Exception:
            pass

        bot.send_message(
            user_id, 
            "✅ 𝗢𝗥𝗗𝗘𝗥 𝗜𝗗 𝗚𝗥𝗢𝗛𝗢𝗡 𝗞𝗢𝗥𝗔 𝗛𝗢𝗬𝗘𝗖𝗛𝗘!\n\n📸 𝗘𝗞𝗛𝗢𝗡 𝗔𝗣𝗡𝗔𝗥 𝗕𝗜𝗡𝗔𝗡𝗖𝗘 𝗣𝗔𝗬𝗠𝗘𝗡𝗧-𝗘𝗥 𝗦𝗖𝗥𝗘𝗘𝗡𝗦𝗛𝗢𝗧 𝗖𝗛𝗢𝗕𝗜 𝗔𝗞𝗔𝗥𝗘 𝗣𝗔𝗧𝗛𝗔𝗡:", 
            reply_markup=main_menu()
        )

    elif user_state.get(user_id, {}).get("step") == "waiting_bkash":
        user_state[user_id]["bkash_number"] = text
        data = user_state[user_id]
        user_state[user_id]["step"] = "completed"

        summary_msg = (
            f"🌙 𝗔𝗦𝗦𝗔𝗟𝗔𝗠𝗨 𝗔𝗟𝗔𝗜𝗞𝗨𝗠\n"
            f"👤 𝗜'𝗠 𝗦𝗔𝗜𝗠\n"
            f"👑 𝗔𝗗𝗠𝗜𝗡 𝗢𝗙 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧 ⚡\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎉 𝗔𝗣𝗡𝗔𝗥 𝗢𝗥𝗗𝗘𝗥 𝗦𝗨𝗕𝗠𝗜𝗧 𝗛𝗢𝗬𝗘𝗖𝗛𝗘!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 𝗗𝗢𝗟𝗟𝗔𝗥: {data['amount']} 𝗨𝗦𝗗\n"
            f"💰 𝗧𝗔𝗞𝗔: {data['total_taka']} 𝗕𝗗𝗧\n"
            f"🆔 𝗢𝗥𝗗𝗘𝗥 𝗜𝗗: {data['order_id']}\n"
            f"📱 𝗕𝗞𝗔𝗦𝗛 𝗡𝗨𝗠𝗕𝗘𝗥: {data['bkash_number']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏳ 15 𝗠𝗜𝗡 𝗢𝗣𝗘𝗞𝗞𝗛𝗔 𝗞𝗢𝗥𝗨𝗡. 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗦𝗢𝗠𝗣𝗢𝗡𝗡𝗢 𝗛𝗢𝗟𝗘 𝗦𝗠𝗦 𝗣𝗔𝗕𝗘𝗡."
        )
        bot.send_message(user_id, summary_msg, reply_markup=main_menu())

        admin_notification = (
            f"🚨 𝗡𝗢𝗧𝗨𝗡 𝗗𝗢𝗟𝗟𝗔𝗥 𝗦𝗘𝗟𝗟 𝗢𝗥𝗗𝗘𝗥 𝗘𝗦𝗘𝗖𝗛𝗘! 🚨\n\n"
            f"👤 𝗨𝗦𝗘𝗥 𝗜𝗗: {user_id}\n"
            f"💵 𝗗𝗢𝗟𝗟𝗔𝗥: {data['amount']} 𝗨𝗦𝗗\n"
            f"💱 𝗧𝗔𝗞𝗔: {data['total_taka']} 𝗕𝗗𝗧\n"
            f"🆔 𝗢𝗥𝗗𝗘𝗥 𝗜𝗗: {data['order_id']}\n"
            f"📱 𝗕𝗞𝗔𝗦𝗛: {data['bkash_number']}"
        )
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘", callback_data=f"app_{user_id}"),
            types.InlineKeyboardButton("❌ 𝗖𝗔𝗡𝗖𝗘𝗟", callback_data=f"rej_{user_id}")
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
            "✅ 𝗦𝗖𝗥𝗘𝗘𝗡𝗦𝗛𝗢𝗧 𝗦𝗢𝗡𝗚𝗥𝗢𝗞𝗞𝗛𝗢𝗡 𝗞𝗢𝗥𝗔 𝗛𝗢𝗬𝗘𝗖𝗛𝗘!\n\n"
            "💳 𝗘𝗞𝗛𝗢𝗡 𝗔𝗣𝗡𝗔𝗥 𝗝𝗘 𝗕𝗞𝗔𝗦𝗛 𝗡𝗨𝗠𝗕𝗘𝗥-𝗘 𝗧𝗔𝗞𝗔 𝗡𝗜𝗧𝗘 𝗖𝗛𝗔𝗡 𝗧𝗔 𝗡𝗜𝗖𝗛𝗘 𝗟𝗜𝗞𝗛𝗘 𝗣𝗔𝗧𝗛𝗔𝗡:",
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
            "✏️ 𝗔𝗣𝗡𝗜 𝗞𝗢𝗧𝗢 𝗗𝗢𝗟𝗟𝗔𝗥 (𝗨𝗦𝗗) 𝗦𝗘𝗟𝗟 𝗞𝗢𝗥𝗧𝗘 𝗖𝗛𝗔𝗡?\n"
            "𝗗𝗢𝗬𝗔 𝗞𝗢𝗥𝗘 𝗦𝗛𝗨𝗗𝗛𝗨 𝗦𝗢𝗡𝗚𝗞𝗛𝗔-𝗧𝗜 (𝗝𝗘𝗠𝗢𝗡: 10 𝗕𝗔 50) 𝗡𝗜𝗖𝗛𝗘 𝗟𝗜𝗞𝗛𝗘 𝗣𝗔𝗧𝗛𝗔𝗡:"
        )
        return

    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ 𝗘𝗜 𝗞𝗔𝗝 𝗞𝗢𝗥𝗔𝗥 𝗣𝗘𝗥𝗠𝗜𝗦𝗦𝗜𝗢𝗡 𝗔𝗣𝗡𝗔𝗥 𝗡𝗘𝗜!", show_alert=True)
        return

    if data.startswith("app_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "𝗢𝗥𝗗𝗘𝗥 𝗔𝗣𝗣𝗥𝗢𝗩𝗘 𝗞𝗢𝗥𝗔 𝗛𝗢𝗬𝗘𝗖𝗛𝗘!")
        bot.send_message(
            target_user, 
            "🎉 𝗔𝗦𝗦𝗔𝗟𝗔𝗠𝗨 𝗔𝗟𝗔𝗜𝗞𝗨𝗠\n"
            "👤 𝗜'𝗠 𝗦𝗔𝗜𝗠\n"
            "👑 𝗔𝗗𝗠𝗜𝗡 𝗢𝗙 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧 ⚡\n\n"
            "✅ 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟\n"
            "𝗥𝗘𝗤𝗨𝗘𝗦𝗧𝗘𝗗 𝗙𝗨𝗡𝗗𝗦 𝗛𝗔𝗩𝗘 𝗕𝗘𝗘𝗡 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬 𝗦𝗘𝗡𝗧 𝗧𝗢 𝗬𝗢𝗨𝗥 𝗣𝗥𝗢𝗩𝗜𝗗𝗘𝗗 𝗡𝗨𝗠𝗕𝗘𝗥.", 
            reply_markup=main_menu()
        )
        try:
            bot.edit_message_caption(caption=call.message.caption + "\n\n✅ 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 & 𝗣𝗔𝗜𝗗", chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception:
            bot.edit_message_text(text=call.message.text + "\n\n✅ 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 & 𝗣𝗔𝗜𝗗", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data.startswith("rej_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "𝗢𝗥𝗗𝗘𝗥 𝗥𝗘𝗝𝗘𝗖𝗧 𝗞𝗢𝗥𝗔 𝗛𝗢𝗬𝗘𝗖𝗛𝗘.")
        bot.send_message(
            target_user, 
            "⚠️ 𝗦𝗢𝗧𝗢𝗥𝗞𝗢𝗕𝗔𝗥𝗧𝗔! 𝗔𝗣𝗡𝗔𝗥 𝗢𝗥𝗗𝗘𝗥-𝗧𝗜 𝗥𝗘𝗝𝗘𝗖𝗧 𝗞𝗢𝗥𝗔 𝗛𝗢𝗬𝗘𝗖𝗛𝗘. 𝗦𝗢𝗧𝗛𝗜𝗞 𝗧𝗢𝗧𝗧𝗛𝗢 𝗗𝗜𝗬𝗘 𝗔𝗕𝗔𝗥 𝗖𝗛𝗘𝗦𝗧𝗔 𝗞𝗢𝗥𝗨𝗡.", 
            reply_markup=main_menu()
        )
        try:
            bot.edit_message_caption(caption=call.message.caption + "\n\n❌ 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗥𝗘𝗝𝗘𝗖𝗧𝗘𝗗", chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception:
            bot.edit_message_text(text=call.message.text + "\n\n❌ 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗥𝗘𝗝𝗘𝗖𝗧𝗘𝗗", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data == "admin_toggle":
        bot_status["is_active"] = not bot_status["is_active"]
        status_text = "𝗔𝗖𝗧𝗜𝗩𝗘" if bot_status["is_active"] else "𝗢𝗙𝗙"
        bot.answer_callback_query(call.id, f"𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗨𝗦: {status_text}", show_alert=True)

    elif data == "admin_rate":
        bot.answer_callback_query(call.id, f"𝗕𝗢𝗥𝗧𝗢𝗠𝗔𝗡 𝗥𝗔𝗧𝗘: {DOLAR_RATE} 𝗧𝗔𝗞𝗔", show_alert=True)

    elif data == "admin_broadcast":
        user_state[ADMIN_ID] = {"step": "waiting_broadcast"}
        bot.send_message(ADMIN_ID, "📢 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗠𝗘𝗦𝗦𝗔𝗚𝗘-𝗧𝗜 𝗟𝗜𝗞𝗛𝗘 𝗣𝗔𝗧𝗛𝗔𝗡:")

if __name__ == "__main__":
    print("Bot is starting on Railway...")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
