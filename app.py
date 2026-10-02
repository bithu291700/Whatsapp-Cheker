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

bot = telebot.TeleBot(TOKEN)

user_state = {}
bot_status = {"is_active": True}

# Prodhan Menu (Reply Keyboard)
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
        bot.reply_to(message, "⚠️ 𝐃𝐮𝐤𝐤𝐡𝐢𝐭𝐨! 𝐁𝐨𝐫𝐭𝐨𝐦𝐚𝐧𝐞 𝐚𝐦𝐚𝐝𝐞𝐫 𝐬𝐞𝐫𝐯𝐢𝐜𝐞 𝐬𝐨𝐦𝐨𝐲𝐚𝐬𝐬𝐡𝐨 𝐯𝐚𝐛𝐞 𝐛𝐨𝐧𝐝𝐡𝐨 𝐫𝐨𝐲𝐞𝐜𝐡𝐞.")
        return
    
    user_state.pop(message.from_user.id, None)
    welcome_text = (
        f"🌟 𝐏𝐫𝐞𝐦𝐢𝐮𝐦 𝐃𝐨𝐥𝐥𝐚𝐫 𝐄𝐱𝐜𝐡𝐚𝐧𝐠𝐞 𝐙𝐨𝐧𝐞 𝐞 𝐚𝐩𝐧𝐚𝐤𝐞 𝐬𝐡𝐚𝐠𝐨𝐭𝐨𝐦! 🌟\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💱 𝐁𝐨𝐫𝐭𝐨𝐦𝐚𝐧 𝐑𝐚𝐭𝐞: 𝟏 𝐔𝐒𝐃 = {DOLAR_RATE} 𝐓𝐚𝐤𝐚\n"
        f"⚡ 𝐒𝐡𝐞𝐛𝐚: 𝐃𝐫𝐮𝐭𝐨 𝐨 𝐬𝐡𝐨𝐧𝐠𝐩𝐮𝐫𝐧𝐨 𝐧𝐢𝐫𝐚𝐩𝐨𝐝 𝐥𝐞𝐧-𝐝𝐞𝐧.\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👇 𝐀𝐩𝐧𝐚𝐫 𝐩𝐫𝐨𝐲𝐨𝐣𝐨𝐧𝐢𝐨 𝐨𝐩𝐭𝐢𝐨𝐧-𝐭𝐢 𝐧𝐢𝐜𝐡 𝐭𝐡𝐞𝐤𝐞 𝐬𝐞𝐥𝐞𝐜𝐭 𝐤𝐨𝐫𝐮𝐧:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text

    if not bot_status["is_active"] and user_id != ADMIN_ID:
        bot.reply_to(message, "⚠️ 𝐁𝐨𝐭-𝐭𝐢 𝐛𝐨𝐫𝐭𝐨𝐦𝐚𝐧𝐞 𝐨𝐟𝐟𝐥𝐢𝐧𝐞 𝐫𝐨𝐲𝐞𝐜𝐡𝐞.")
        return

    if text == "💵 𝐒𝐄𝐋𝐋 𝐃𝐎𝐋𝐋𝐄𝐑":
        # শুধু Binance অপশন সহ ইনলাইন কিবোর্ড তৈরি করা হলো
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Binance", callback_data="binance_sell_option"))
        
        msg = (
            f"🎉 𝐎𝐯𝐡𝐢𝐧𝐨𝐧𝐝𝐨𝐧! 𝐀𝐩𝐧𝐢 𝐚𝐦𝐚𝐝𝐞𝐫 𝐬𝐚𝐭𝐡𝐞 𝐬𝐡𝐨𝐟𝐨𝐥𝐯𝐚𝐛𝐞 𝐝𝐨𝐥𝐥𝐚𝐫 𝐬𝐞𝐥𝐥 𝐤𝐨𝐫𝐚 𝐬𝐡𝐮𝐫𝐮 𝐤𝐨𝐫𝐞𝐜𝐡𝐞𝐧.\n\n"
            f"📈 𝐁𝐨𝐫𝐭𝐨𝐦𝐚𝐧 𝐞𝐱𝐜𝐡𝐚𝐧𝐠𝐞 𝐫𝐚𝐭𝐞: {DOLAR_RATE} 𝐓𝐚𝐤𝐚 / 𝐔𝐒𝐃\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👇 𝐃𝐨𝐲𝐚 𝐤𝐨𝐫𝐞 𝐧𝐢𝐜𝐡𝐞𝐫 𝐛𝐮𝐭𝐭𝐨𝐧-𝐞 𝐜𝐥𝐢𝐤 𝐤𝐨𝐫𝐮𝐧:"
        )
        bot.send_message(user_id, msg, reply_markup=markup)

    elif text == "📞 𝐒𝐔𝐏𝐏𝐎𝐑𝐓":
        user_state.pop(user_id, None)
        support_msg = (
            f"🛠 𝐂𝐮𝐬𝐭𝐨𝐦𝐞𝐫 𝐒𝐮𝐩𝐩𝐨𝐫𝐭 & 𝐇𝐞𝐥𝐩 𝐃𝐞𝐬𝐤\n\n"
            f"𝐉𝐞𝐤𝐨𝐧𝐨 𝐩𝐫𝐨𝐲𝐨𝐣𝐨𝐧𝐞 𝐚𝐦𝐚𝐝𝐞𝐫 𝐨𝐟𝐟𝐢𝐜𝐢𝐚𝐥 𝐚𝐝𝐦𝐢𝐧-𝐞𝐫 𝐬𝐚𝐭𝐡𝐞 𝐣𝐨𝐠𝐚𝐣𝐨𝐠 𝐤𝐨𝐫𝐮𝐧:\n\n"
            f"👤 𝐀𝐝𝐦𝐢𝐧 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞: @{ADMIN_USERNAME}"
        )
        bot.send_message(user_id, support_msg, reply_markup=main_menu())

    elif text == "👑 𝐀𝐃𝐌𝐈𝐍 𝐏𝐀𝐍𝐄𝐋":
        if user_id != ADMIN_ID:
            bot.send_message(user_id, f"❌ 𝐀𝐩𝐧𝐚𝐫 𝐞𝐢 𝐩𝐚𝐧𝐞𝐥 𝐛𝐚𝐛𝐨𝐡𝐚𝐫 𝐤𝐨𝐫𝐚𝐫 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧 𝐧𝐞𝐢!\n\n𝐀𝐩𝐧𝐚𝐫 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐔𝐬𝐞𝐫 𝐈𝐃: {user_id}", reply_markup=main_menu())
            return
        
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("📢 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭", callback_data="admin_broadcast"),
            types.InlineKeyboardButton("💱 𝐑𝐚𝐭𝐞 𝐂𝐡𝐚𝐧𝐠𝐞", callback_data="admin_rate"),
            types.InlineKeyboardButton("🔄 𝐁𝐨𝐭 𝐎𝐧/𝐎𝐟𝐟", callback_data="admin_toggle")
        )
        bot.send_message(user_id, "👑 𝐀𝐝𝐦𝐢𝐧 𝐂𝐨𝐧𝐭𝐫𝐨𝐥 𝐏𝐚𝐧𝐞𝐥\n\n𝐍𝐢𝐜𝐡𝐞𝐫 𝐨𝐩𝐭𝐢𝐨𝐧-𝐠𝐮𝐥𝐨 𝐭𝐡𝐞𝐤𝐞 𝐤𝐚𝐣 𝐬𝐞𝐥𝐞𝐜𝐭 𝐤𝐨𝐫𝐮𝐧:", reply_markup=admin_markup)

    elif user_state.get(user_id, {}).get("step") == "waiting_broadcast":
        if user_id == ADMIN_ID:
            user_state.pop(user_id, None)
            bot.send_message(user_id, f"✅ 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐬𝐡𝐨𝐟𝐨𝐥𝐯𝐚𝐛𝐞 𝐬𝐨𝐦𝐩𝐨𝐧𝐧𝐨 𝐡𝐨𝐲𝐞𝐜𝐡𝐞!\n\n𝐁𝐚𝐫𝐭𝐚:\n{text}", reply_markup=main_menu())

    elif user_state.get(user_id, {}).get("step") == "waiting_amount":
        try:
            amount = float(text)
            total_taka = amount * DOLAR_RATE
            user_state[user_id]["amount"] = amount
            user_state[user_id]["total_taka"] = total_taka
            user_state[user_id]["step"] = "waiting_order_id"

            # ইউজারের পাঠানো সংখ্যা লেখার মেসেজটি ভ্যানিশ করার চেষ্টা
            try:
                bot.delete_message(user_id, message.message_id)
            except Exception:
                pass

            binance_msg = (
                f"✅ 𝐀𝐩𝐧𝐢 𝐬𝐞𝐥𝐥 𝐤𝐨𝐫𝐭𝐞 𝐜𝐡𝐚𝐜𝐜𝐡𝐞𝐧: {amount} 𝐔𝐒𝐃\n"
                f"💰 𝐀𝐩𝐧𝐢 𝐩𝐚𝐛𝐞𝐧: {total_taka} 𝐓𝐚𝐤𝐚\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💎 𝐏𝐚𝐲𝐦𝐞𝐧𝐭 𝐍𝐢𝐫𝐝𝐞𝐬𝐡𝐢𝐤𝐚:\n"
                f"𝐃𝐨𝐲𝐚 𝐤𝐨𝐫𝐞 𝐧𝐢𝐜𝐡𝐞𝐫 𝐁𝐢𝐧𝐚𝐧𝐜𝐞 𝐏𝐚𝐲 𝐈𝐃 𝐭𝐞 𝐝𝐨𝐥𝐥𝐚𝐫 𝐬𝐞𝐧𝐝 𝐤𝐨𝐫𝐮𝐧:\n\n"
                f"🆔 𝐁𝐢𝐧𝐚𝐧𝐜𝐞 𝐏𝐚𝐲 𝐈𝐃: {BINANCE_ID}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📥 𝐃𝐨𝐥𝐥𝐚𝐫 𝐩𝐚𝐭𝐡𝐚𝐧𝐨𝐫 𝐩𝐨𝐫 𝐎𝐫𝐝𝐞𝐫 𝐈𝐃 (𝐓𝐗𝐈𝐃) 𝐭𝐢 𝐞𝐤𝐡𝐚𝐧𝐞 𝐥𝐢𝐤𝐡𝐞 𝐩𝐚𝐭𝐡𝐚𝐧:"
            )
            bot.send_message(user_id, binance_msg, reply_markup=main_menu())
        except ValueError:
            bot.send_message(user_id, "⚠️ 𝐃𝐨𝐲𝐚 𝐤𝐨𝐫𝐞 𝐬𝐨𝐭𝐡𝐢𝐤 𝐬𝐡𝐨𝐧𝐠𝐤𝐡𝐚 𝐥𝐢𝐤𝐡𝐮𝐧 (𝐣𝐞𝐦𝐨𝐧: 𝟏𝟎 𝐛𝐚 𝟐𝟎)", reply_markup=main_menu())

    elif user_state.get(user_id, {}).get("step") == "waiting_order_id":
        user_state[user_id]["order_id"] = text
        user_state[user_id]["step"] = "waiting_screenshot"
        bot.send_message(user_id, "✅ 𝐎𝐫𝐝𝐞𝐫 𝐈𝐃 𝐠𝐫𝐨𝐡𝐨𝐧 𝐤𝐨𝐫𝐚 𝐡𝐨𝐲𝐞𝐜𝐡𝐞!\n\n📸 𝐄𝐤𝐡𝐨𝐧 𝐚𝐩𝐧𝐚𝐫 𝐁𝐢𝐧𝐚𝐧𝐜𝐞 𝐏𝐚𝐲𝐦𝐞𝐧𝐭-𝐞𝐫 𝐬𝐜𝐫𝐞𝐞𝐧𝐬𝐡𝐨𝐭 𝐜𝐡𝐨𝐛𝐢 𝐚𝐤𝐚𝐫𝐞 𝐩𝐚𝐭𝐡𝐚𝐧:", reply_markup=main_menu())

    elif user_state.get(user_id, {}).get("step") == "waiting_bkash":
        user_state[user_id]["bkash_number"] = text
        data = user_state[user_id]
        user_state[user_id]["step"] = "completed"

        summary_msg = (
            f"🎉 𝐀𝐩𝐧𝐚𝐫 𝐨𝐫𝐝𝐞𝐫-𝐭𝐢 𝐬𝐡𝐨𝐟𝐨𝐥𝐯𝐚𝐛𝐞 𝐬𝐮𝐛𝐦𝐢𝐭 𝐡𝐨𝐲𝐞𝐜𝐡𝐞!\n\n"
            f"💵 𝐃𝐨𝐥𝐥𝐚𝐫: {data['amount']} 𝐔𝐒𝐃\n"
            f"💰 𝐓𝐚𝐤𝐚: {data['total_taka']} 𝐁𝐃𝐓\n"
            f"🆔 𝐎𝐫𝐝𝐞𝐫 𝐈𝐃: {data['order_id']}\n"
            f"📱 𝐁𝐤𝐚𝐬𝐡 𝐍𝐮𝐦𝐛𝐞𝐫: {data['bkash_number']}\n\n"
            f"⏳ 𝟏𝟓 𝐦𝐢𝐧𝐢𝐭 𝐨𝐩𝐞𝐤𝐤𝐡𝐚 𝐤𝐨𝐫𝐮𝐧. 𝐏𝐚𝐲𝐦𝐞𝐧𝐭 𝐬𝐨𝐦𝐩𝐨𝐧𝐧𝐨 𝐡𝐨𝐥𝐞 𝐒𝐌𝐒 𝐩𝐚𝐛𝐞𝐧."
        )
        bot.send_message(user_id, summary_msg, reply_markup=main_menu())

        admin_notification = (
            f"🚨 𝐍𝐨𝐭𝐮𝐧 𝐃𝐨𝐥𝐥𝐚𝐫 𝐒𝐞𝐥𝐥 𝐎𝐫𝐝𝐞𝐫 𝐄𝐬𝐞𝐜𝐡𝐞! 🚨\n\n"
            f"👤 𝐔𝐬𝐞𝐫 𝐈𝐃: {user_id}\n"
            f"💵 𝐃𝐨𝐥𝐥𝐚𝐫: {data['amount']} 𝐔𝐒𝐃\n"
            f"💱 𝐓𝐚𝐤𝐚: {data['total_taka']} 𝐁𝐃𝐓\n"
            f"🆔 𝐎𝐫𝐝𝐞𝐫 𝐈𝐃: {data['order_id']}\n"
            f"📱 𝐛𝐊𝐚𝐬𝐡: {data['bkash_number']}"
        )
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("✅ 𝐀𝐩𝐩𝐫𝐨𝐯𝐞", callback_data=f"app_{user_id}"),
            types.InlineKeyboardButton("❌ 𝐂𝐚𝐧𝐜𝐞𝐥", callback_data=f"rej_{user_id}")
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
        
        bot.send_message(
            user_id, 
            "✅ 𝐒𝐜𝐫𝐞𝐞𝐧𝐬𝐡𝐨𝐭 𝐬𝐡𝐨𝐧𝐠𝐫𝐨𝐤𝐤𝐡𝐨𝐧 𝐤𝐨𝐫𝐚 𝐡𝐨𝐲𝐞𝐜𝐡𝐞!\n\n"
            "💳 𝐄𝐤𝐡𝐨𝐧 𝐚𝐩𝐧𝐚𝐫 𝐣𝐞 𝐛𝐤𝐚𝐬𝐡 𝐧𝐮𝐦𝐛𝐞𝐫-𝐞 𝐭𝐚𝐤𝐚 𝐧𝐢𝐭𝐞 𝐜𝐡𝐚𝐧 𝐭𝐚 𝐧𝐢𝐜𝐡𝐞 𝐥𝐢𝐤𝐡𝐞 𝐩𝐚𝐭𝐡𝐚𝐧:",
            reply_markup=main_menu()
        )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global DOLAR_RATE
    user_id = call.from_user.id
    data = call.data

    # Binance অপশন বাটনে ক্লিক করার হ্যান্ডলার
    if data == "binance_sell_option":
        bot.answer_callback_query(call.id)
        
        # আগের মেনু মেসেজটি ভ্যানিশ বা ডিলিট করে দেওয়া
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            print(e)
            
        # ইউজারের স্টেট সেট করা যাতে পরবর্তী লেখাটি অ্যামাউন্ট হিসেবে ধরে
        user_state[user_id] = {"step": "waiting_amount"}
        
        bot.send_message(
            user_id, 
            "✏️ 𝐀𝐩𝐧𝐢 𝐤𝐨𝐭𝐨 𝐝𝐨𝐥𝐥𝐚𝐫 (𝐔𝐒𝐃) 𝐬𝐞𝐥𝐥 𝐤𝐨𝐫𝐭𝐞 𝐜𝐡𝐚𝐧?\n"
            "𝐃𝐨𝐲𝐚 𝐤𝐨𝐫𝐞 𝐬𝐡𝐮𝐝𝐡𝐮 𝐬𝐡𝐨𝐧𝐠𝐤𝐡𝐚-𝐭𝐢 (𝐣𝐞𝐦𝐨𝐧: 𝟏𝟎 𝐛𝐚 𝟓𝟎) 𝐧𝐢𝐜𝐡𝐞 𝐥𝐢𝐤𝐡𝐞 𝐩𝐚𝐭𝐡𝐚𝐧:"
        )
        return

    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ 𝐄𝐢 𝐤𝐚𝐣 𝐤𝐨𝐫𝐚𝐫 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧 𝐚𝐩𝐧𝐚𝐫 𝐧𝐞𝐢!", show_alert=True)
        return

    if data.startswith("app_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "𝐎𝐫𝐝𝐞𝐫 𝐚𝐩𝐩𝐫𝐨𝐯𝐞 𝐤𝐨𝐫𝐚 𝐡𝐨𝐲𝐞𝐜𝐡𝐞!")
        bot.send_message(
            target_user, 
            "🎉 𝐎𝐯𝐡𝐢𝐧𝐨𝐧𝐝𝐨𝐧! 𝐀𝐩𝐧𝐚𝐫 𝐝𝐨𝐥𝐥𝐚𝐫 𝐨𝐫𝐝𝐞𝐫-𝐭𝐢 𝐯𝐞𝐫𝐢𝐟𝐲 𝐨 𝐩𝐚𝐲𝐦𝐞𝐧𝐭 𝐬𝐨𝐦𝐩𝐨𝐧𝐧𝐨 𝐡𝐨𝐲𝐞𝐜𝐡𝐞.", 
            reply_markup=main_menu()
        )
        try:
            bot.edit_message_caption(caption=call.message.caption + "\n\n✅ 𝐒𝐓𝐀𝐓𝐔𝐒: 𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 & 𝐏𝐀𝐈𝐃", chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception:
            bot.edit_message_text(text=call.message.text + "\n\n✅ 𝐒𝐓𝐀𝐓𝐔𝐒: 𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 & 𝐏𝐀𝐈𝐃", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data.startswith("rej_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "𝐎𝐫𝐝𝐞𝐫 𝐫𝐞𝐣𝐞𝐜𝐭 𝐤𝐨𝐫𝐚 𝐡𝐨𝐲𝐞𝐜𝐡𝐞.")
        bot.send_message(
            target_user, 
            "⚠️ 𝐒𝐨𝐭𝐨𝐫𝐤𝐨𝐛𝐚𝐫𝐭𝐚! 𝐀𝐩𝐧𝐚𝐫 𝐨𝐫𝐝𝐞𝐫-𝐭𝐢 𝐫𝐞𝐣𝐞𝐜𝐭 𝐤𝐨𝐫𝐚 𝐡𝐨𝐲𝐞𝐜𝐡𝐞. 𝐒𝐨𝐭𝐡𝐢𝐤 𝐭𝐨𝐭𝐭𝐡𝐨 𝐝𝐢𝐲𝐞 𝐚𝐛𝐚𝐫 𝐜𝐡𝐞𝐬𝐭𝐚 𝐤𝐨𝐫𝐮𝐧.", 
            reply_markup=main_menu()
        )
        try:
            bot.edit_message_caption(caption=call.message.caption + "\n\n❌ 𝐒𝐓𝐀𝐓𝐔𝐒: 𝐑𝐄𝐉𝐄𝐂𝐓𝐄𝐃", chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception:
            bot.edit_message_text(text=call.message.text + "\n\n❌ 𝐒𝐓𝐀𝐓𝐔𝐒: 𝐑𝐄𝐉𝐄𝐂𝐓𝐄𝐃", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data == "admin_toggle":
        bot_status["is_active"] = not bot_status["is_active"]
        status_text = "𝐀𝐜𝐭𝐢𝐯𝐞" if bot_status["is_active"] else "𝐎𝐟𝐟"
        bot.answer_callback_query(call.id, f"𝐁𝐨𝐭 𝐒𝐭𝐚𝐭𝐮𝐬: {status_text}", show_alert=True)

    elif data == "admin_rate":
        bot.answer_callback_query(call.id, f"𝐁𝐨𝐫𝐭𝐨𝐦𝐚𝐧 𝐑𝐚𝐭𝐞: {DOLAR_RATE} 𝐓𝐚𝐤𝐚", show_alert=True)

    elif data == "admin_broadcast":
        user_state[ADMIN_ID] = {"step": "waiting_broadcast"}
        bot.send_message(ADMIN_ID, "📢 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐦𝐞𝐬𝐬𝐚𝐠𝐞-𝐭𝐢 𝐥𝐢𝐤𝐡𝐞 𝐩𝐚𝐭𝐡𝐚𝐧:")

if __name__ == "__main__":
    print("Bot is starting on Railway...")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
