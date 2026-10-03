import os
import telebot
from telebot import types

TOKEN = os.environ.get('BOT_TOKEN')

ADMIN_ID = 7388500439          
BINANCE_ID = "123456789"       
ADMIN_USERNAME = "SAIM_X9"     
DOLAR_RATE = 120.0             

bot = telebot.TeleBot(TOKEN)

user_state = {}
bot_status = {"is_active": True}

# **Premium Custom Emoji IDs (আপনার দেওয়া আইডিগুলো দিয়ে সেট করা)**
E_HAND = '<a href="tg://emoji?id=5269657987219232606">🤲</a>'
E_CHECK = '<a href="tg://emoji?id=5206607081334906820">✅</a>'
E_STAR = '<a href="tg://emoji?id=5269215244810491516">🌟</a>'
E_CHART = '<a href="tg://emoji?id=5231159755803761138">📈</a>'
E_MONEY = '<a href="tg://emoji?id=5411225014148014586">💵</a>'
E_CROSS = '<a href="tg://emoji?id=5210952531676504517">❌</a>'
E_DIAMOND = '<a href="tg://emoji?id=5240241223632954241">💎</a>'
E_TOOL = '<a href="tg://emoji?id=5341715473882955310">🛠</a>'
E_WARNING = '<a href="tg://emoji?id=5447644880824161073">⚠</a>'
E_INBOX = '<a href="tg://emoji?id=5323442290709895472">📥</a>'
E_CAMERA = '<a href="tg://emoji?id=584602487033353251">📸</a>'
E_BANK = '<a href="tg://emoji?id=5967456680940671207">🏦</a>'
E_PHONE = '<a href="tg://emoji?id=5388632425314140043">📱</a>'
E_CLOCK = '<a href="tg://emoji?id=5440621591387980068">⏳</a>'
E_ALERT = '<a href="tg://emoji?id=5879813604082983587">🚨</a>'
E_EXCHANGE = '<a href="tg://emoji?id=577184941154078090">💱</a>'
E_CROWN = '<a href="tg://emoji?id=541565581407923871">👑</a>'
E_USER = '<a href="tg://emoji?id=597770735999717115">👤</a>'
E_POINT = '<a href="tg://emoji?id=5449683594425410231">👇</a>'

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # টেলিগ্রামের নিয়ম অনুযায়ী ReplyKeyboardMarkup-এর বোতামে শুধু টেক্সট বা সাধারণ ইমোজি কাজ করে, তাই এখানে পরিষ্কার স্ট্যান্ডার্ড ইমোজি রাখা হয়েছে যাতে ক্র্যাশ না করে
    btn_sell = types.KeyboardButton(f"💵 𝗦𝗘𝗟𝗟 𝗗𝗢𝗟𝗟𝗘𝗥")
    btn_support = types.KeyboardButton(f"🛠 𝗦𝗨𝗣𝗣𝗢𝗥𝗧")
    btn_admin = types.KeyboardButton(f"👑 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟")
    markup.add(btn_sell, btn_support, btn_admin)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not bot_status["is_active"] and message.from_user.id != ADMIN_ID:
        bot.reply_to(message, f"{E_WARNING} 𝗗𝗨𝗞𝗞𝗛𝗜𝗧𝗢! 𝗕𝗢𝗥𝗧𝗢𝗠𝗔𝗡𝗘 𝗔𝗠𝗔𝗗𝗘𝗥 𝗦𝗘𝗥𝗩𝗜𝗖𝗘 𝗕𝗢𝗡𝗗𝗛𝗢 𝗥𝗢𝗬𝗘𝗖𝗛𝗘.", parse_mode="HTML")
        return
    
    user_state.pop(message.from_user.id, None)
    welcome_text = (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_HAND} 𝗔𝗦𝗦𝗔𝗟𝗔𝗠𝗨 𝗔𝗟𝗔𝗜𝗞𝗨𝗠\n"
        f"{E_USER} 𝗜'𝗠 𝗦𝗔𝗜𝗠\n"
        f"{E_CROWN} 𝗔𝗗𝗠𝗜𝗡 𝗢𝗙 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{E_STAR} 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧 𝗭𝗢𝗡𝗘!\n"
        f"{E_EXCHANGE} 𝗥𝗔𝗧𝗘: 1 𝗨𝗦𝗗 = {DOLAR_RATE} 𝗕𝗗𝗧\n\n"
        f"{E_POINT} 𝗣𝗟𝗘𝗔𝗦𝗘 𝗦𝗘𝗟𝗘𝗖𝗧 𝗔𝗡 𝗢𝗣𝗧𝗜𝗢𝗡:"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="HTML", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text

    if not bot_status["is_active"] and user_id != ADMIN_ID:
        bot.reply_to(message, f"{E_WARNING} 𝗕𝗢𝗧-𝗧𝗜 𝗕𝗢𝗥𝗧𝗢𝗠𝗔𝗡𝗘 𝗢𝗙𝗙𝗟𝗜𝗡𝗘 𝗥𝗢𝗬𝗘𝗖𝗛𝗘.", parse_mode="HTML")
        return

    if "💵 𝗦𝗘𝗟𝗟 𝗗𝗢𝗟𝗟𝗘𝗥" in text:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("𝗕𝗜𝗡𝗔𝗡𝗖𝗘", callback_data="binance_sell_option"))
        markup.add(types.InlineKeyboardButton("⬅️ 𝗕𝗔𝗖𝗞", callback_data="back_to_main_menu"))
        
        msg = (
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_HAND} 𝗔𝗦𝗦𝗔𝗟𝗔𝗠𝗨 𝗔𝗟𝗔𝗜𝗞𝗨𝗠\n"
            f"{E_USER} 𝗜'𝗠 𝗦𝗔𝗜𝗠\n"
            f"{E_CROWN} 𝗔𝗗𝗠𝗜𝗡 𝗢𝗙 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{E_CHART} 𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗥𝗔𝗧𝗘: {DOLAR_RATE} 𝗕𝗗𝗧 / 𝗨𝗦𝗗\n\n"
            f"{E_POINT} 𝗖𝗟𝗜𝗖𝗞 𝗧𝗛𝗘 𝗕𝗨𝗧𝗧𝗢𝗡 𝗕𝗘𝗟𝗢𝗪:"
        )
        remove_markup = types.ReplyKeyboardRemove()
        bot.send_message(user_id, "Menu hidden", reply_markup=remove_markup)
        bot.send_message(user_id, msg, parse_mode="HTML", reply_markup=markup)

    elif "🛠 𝗦𝗨𝗣𝗣𝗢𝗥𝗧" in text:
        user_state.pop(user_id, None)
        support_msg = (
            f"{E_TOOL} 𝗖𝗨𝗦𝗧𝗢𝗠𝗘𝗥 𝗦𝗨𝗣𝗣𝗢𝗥𝗧 & 𝗛𝗘𝗟𝗣 𝗗𝗘𝗦𝗞\n\n"
            f"𝗔𝗗𝗠𝗜𝗡 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘: @{ADMIN_USERNAME}"
        )
        bot.send_message(user_id, support_msg, parse_mode="HTML", reply_markup=main_menu())

    elif "👑 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟" in text:
        if user_id != ADMIN_ID:
            bot.send_message(user_id, f"{E_CROSS} 𝗣𝗘𝗥𝗠𝗜𝗦𝗦𝗜𝗢𝗡 𝗗𝗘𝗡𝗜𝗘𝗗!\n\n𝗨𝗦𝗘𝗥 𝗜𝗗: {user_id}", parse_mode="HTML", reply_markup=main_menu())
            return
        
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("📢 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧", callback_data="admin_broadcast"),
            types.InlineKeyboardButton("🔄 𝗕𝗢𝗧 𝗢𝗡/𝗢𝗙𝗙", callback_data="admin_toggle")
        )
        bot.send_message(user_id, f"{E_CROWN} 𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗡𝗧𝗥𝗢𝗟 𝗣𝗔𝗡𝗘𝗟", parse_mode="HTML", reply_markup=admin_markup)

    elif user_state.get(user_id, {}).get("step") == "waiting_amount":
        try:
            amount = float(text)
            total_taka = amount * DOLAR_RATE
            user_state[user_id]["amount"] = amount
            user_state[user_id]["total_taka"] = total_taka
            user_state[user_id]["step"] = "waiting_order_id"

            try:
                prev_msg_id = user_state[user_id].get("amount_msg_id")
                if prev_msg_id:
                    bot.delete_message(user_id, prev_msg_id)
            except Exception:
                pass

            try:
                bot.delete_message(user_id, message.message_id)
            except Exception:
                pass

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("⬅️️ 𝗕𝗔𝗖𝗞", callback_data="back_to_main_menu"))

            binance_msg = (
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{E_HAND} 𝗔𝗦𝗦𝗔𝗟𝗔𝗠𝗨 𝗔𝗟𝗔𝗜𝗞𝗨𝗠\n"
                f"{E_USER} 𝗜'𝗠 𝗦𝗔𝗜𝗠\n"
                f"{E_CROWN} 𝗔𝗗𝗠𝗜𝗡 𝗢𝗙 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"{E_CHECK} 𝗦𝗘𝗟𝗟𝗜𝗡𝗚: {amount} 𝗨𝗦𝗗\n"
                f"{E_MONEY} 𝗬𝗢𝗨 𝗪𝗜𝗟𝗟 𝗚𝗘𝗧: {total_taka} 𝗕𝗗𝗧\n\n"
                f"{E_DIAMOND} 𝗕𝗜𝗡𝗔𝗡𝗖𝗘 𝗣𝗔𝗬 𝗜𝗗:\n`{BINANCE_ID}`\n\n"
                f"{E_INBOX} 𝗣𝗟𝗘𝗔𝗦𝗘 𝗘𝗡𝗧𝗘𝗥 𝗬𝗢𝗨𝗥 𝗢𝗥𝗗𝗘𝗥 𝗜𝗗 (𝗧𝗫𝗜𝗗):"
            )
            sent_msg = bot.send_message(user_id, binance_msg, parse_mode="Markdown", reply_markup=markup)
            user_state[user_id]["binance_msg_id"] = sent_msg.message_id
        except ValueError:
            bot.send_message(user_id, f"{E_WARNING} 𝗣𝗟𝗘𝗔𝗦𝗘 𝗘𝗡𝗧𝗘𝗥 𝗔 𝗩𝗔𝗟𝗜𝗗 𝗡𝗨𝗠𝗕𝗘𝗥!", parse_mode="HTML")

    elif user_state.get(user_id, {}).get("step") == "waiting_order_id":
        user_state[user_id]["order_id"] = text
        user_state[user_id]["step"] = "waiting_screenshot"
        
        try:
            prev_msg_id = user_state[user_id].get("binance_msg_id")
            if prev_msg_id:
                bot.delete_message(user_id, prev_msg_id)
        except Exception:
            pass

        try:
            bot.delete_message(user_id, message.message_id)
        except Exception:
            pass

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("✅ 𝗧𝗥𝗔𝗡𝗦𝗔𝗖𝗧𝗜𝗢𝗡 𝗜𝗗", callback_data="dummy_tx"),
            types.InlineKeyboardButton("📸 𝗡𝗘𝗫𝗧 𝗦𝗖𝗥𝗘𝗘𝗡𝗦𝗛𝗢𝗧", callback_data="dummy_sc")
        )
        markup.add(types.InlineKeyboardButton("⬅️ 𝗕𝗔𝗖𝗞", callback_data="back_to_main_menu"))

        sent_msg = bot.send_message(
            user_id, 
            f"━━━━━━━━━━━━━\n"
            f"{E_CHECK} 𝗧𝗥𝗔𝗡𝗦𝗔𝗖𝗧𝗜𝗢𝗡 𝗜𝗗 𝗥𝗘𝗖𝗘𝗜𝗩𝗘𝗗!\n"
            f"━━━━━━━━━━━━━\n\n"
            f"{E_CAMERA} 𝗡𝗢𝗪 𝗣𝗟𝗘𝗔𝗦𝗘 𝗨𝗣𝗟𝗢𝗔𝗗 𝗧𝗛𝗘 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗦𝗖𝗥𝗘𝗘𝗡𝗦𝗛𝗢𝗧 {E_POINT}", 
            parse_mode="HTML",
            reply_markup=markup
        )
        user_state[user_id]["tx_received_msg_id"] = sent_msg.message_id

    elif user_state.get(user_id, {}).get("step") == "waiting_bkash":
        user_state[user_id]["bkash_number"] = text
        data = user_state[user_id]
        user_state[user_id]["step"] = "completed"

        try:
            bot.delete_message(user_id, message.message_id)
        except Exception:
            pass

        summary_msg = (
            f"━━━━━━━━━━━━━\n"
            f"{E_CLOCK} 𝗥𝗘𝗤𝗨𝗘𝗦𝗧 𝗦𝗨𝗕𝗠𝗜𝗧𝗧𝗘𝗗\n"
            f"━━━━━━━━━━━━━\n"
            f"{E_CHECK} 𝗣𝗟𝗘𝗔𝗦𝗘 𝗦𝗧𝗔𝗬 𝗢𝗡𝗟𝗜𝗡𝗘. 𝗬𝗢𝗨𝗥 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗪𝗜𝗟𝗟 𝗕𝗘 𝗦𝗘𝗡𝗧 𝗧𝗢 𝗬𝗢𝗨𝗥 𝗔𝗖𝗖𝗢𝗨𝗡𝗧 𝗦𝗛𝗢𝗥𝗧𝗟𝗬 𝗪𝗜𝗧𝗛𝗜𝗡 𝗔 𝗙𝗘𝗪 𝗠𝗜𝗡𝗨𝗧𝗘𝗦.\n"
            f"━━━━━━━━━━━━━\n\n"
            f"┏━━━━━━━ 🌙 ━━━━━━━┓\n"
            f"{E_HAND} 𝗔𝗦𝗦𝗔𝗟𝗔𝗠𝗨 𝗔𝗟𝗔𝗜𝗞𝗨𝗠\n"
            f"{E_USER} 𝗜'𝗠 𝗦𝗔𝗜𝗠\n"
            f"{E_CROWN} 𝗔𝗗𝗠𝗜𝗡 𝗢𝗙 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧\n"
            f"┗━━━━━━━ ⚡ ━━━━━━━┛"
        )
        bot.send_message(user_id, summary_msg, parse_mode="HTML", reply_markup=main_menu())

        admin_notification = (
            f"{E_ALERT} 𝗡𝗘𝗪 𝗗𝗢𝗟𝗟𝗔𝗥 𝗦𝗘𝗟𝗟 𝗢𝗥𝗗𝗘𝗥! {E_ALERT}\n\n"
            f"{E_USER} 𝗨𝗦𝗘𝗥 𝗜𝗗: {user_id}\n"
            f"{E_MONEY} 𝗗𝗢𝗟𝗟𝗔𝗥: {data['amount']} 𝗨𝗦𝗗\n"
            f"{E_EXCHANGE} 𝗧𝗔𝗞𝗔: {data['total_taka']} 𝗕𝗗𝗧\n"
            f"🆔 𝗢𝗥𝗗𝗘𝗥 𝗜𝗗: {data['order_id']}\n"
            f"{E_PHONE} 𝗕𝗞𝗔𝗦𝗛: {data['bkash_number']}"
        )
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘", callback_data=f"app_{user_id}"),
            types.InlineKeyboardButton("❌ 𝗥𝗘𝗝𝗘𝗖𝗧", callback_data=f"rej_{user_id}")
        )
        
        if data.get("photo_file_id"):
            bot.send_photo(ADMIN_ID, data["photo_file_id"], caption=admin_notification, parse_mode="HTML", reply_markup=admin_markup)
        else:
            bot.send_message(ADMIN_ID, admin_notification, parse_mode="HTML", reply_markup=admin_markup)

    elif user_state.get(user_id, {}).get("step") == "waiting_broadcast" and user_id == ADMIN_ID:
        user_state.pop(ADMIN_ID, None)
        bot.send_message(ADMIN_ID, f"{E_CHECK} 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗦𝗘𝗡𝗧 (Simulation)", parse_mode="HTML", reply_markup=main_menu())

@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    user_id = message.from_user.id
    if user_state.get(user_id, {}).get("step") == "waiting_screenshot":
        user_state[user_id]["photo_file_id"] = message.photo[-1].file_id
        user_state[user_id]["step"] = "waiting_bkash"
        
        try:
            prev_msg_id = user_state[user_id].get("tx_received_msg_id")
            if prev_msg_id:
                bot.delete_message(user_id, prev_msg_id)
        except Exception:
            pass
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💳 𝗔𝗧𝗠 𝗕𝗞𝗔𝗦𝗛", callback_data="atm_bkash"))
        markup.add(types.InlineKeyboardButton("⬅️ 𝗕𝗔𝗖𝗞", callback_data="back_to_main_menu"))

        sent_msg = bot.send_message(
            user_id, 
            f"━━━━━━━━━━━━━\n"
            f"{E_CHECK} 𝗦𝗖𝗥𝗘𝗘𝗡𝗦𝗛𝗢𝗧 𝗥𝗘𝗖𝗘𝗜𝗩𝗘𝗗!\n"
            f"━━━━━━━━━━━━━\n"
            f"{E_BANK} 𝗥𝗘𝗖𝗘𝗜𝗩𝗘 𝗠𝗢𝗡𝗘𝗬 𝗩𝗜𝗔\n"
            f"━━━━━━━━━━━━━\n"
            f"{E_POINT} 𝗦𝗘𝗟𝗘𝗖𝗧 𝗪𝗛𝗘𝗥𝗘 𝗬𝗢𝗨 𝗪𝗔𝗡𝗧 𝗧𝗢 𝗥𝗘𝗖𝗘𝗜𝗩𝗘 𝗬𝗢𝗨𝗥 𝗙𝗨𝗡𝗗𝗦:", 
            parse_mode="HTML",
            reply_markup=markup
        )
        user_state[user_id]["bkash_prompt_msg_id"] = sent_msg.message_id

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global DOLAR_RATE
    user_id = call.from_user.id
    data = call.data

    if data == "back_to_main_menu":
        bot.answer_callback_query(call.id, "Returned to Main Menu")
        user_state.pop(user_id, None)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        
        welcome_text = (
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_HAND} 𝗔𝗦𝗦𝗔𝗟𝗔𝗠𝗨 𝗔𝗟𝗔𝗜𝗞𝗨𝗠\n"
            f"{E_USER} 𝗜'𝗠 𝗦𝗔𝗜𝗠\n"
            f"{E_CROWN} 𝗔𝗗𝗠𝗜𝗡 𝗢𝗙 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{E_STAR} 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧 𝗭𝗢𝗡𝗘!\n"
            f"{E_EXCHANGE} 𝗥𝗔𝗧𝗘: 1 𝗨𝗦𝗗 = {DOLAR_RATE} 𝗕𝗗𝗧\n\n"
            f"{E_POINT} 𝗣𝗟𝗘𝗔𝗦𝗘 𝗦𝗘𝗟𝗘𝗖𝗧 𝗔𝗡 𝗢𝗣𝗧𝗜𝗢𝗡:"
        )
        bot.send_message(user_id, welcome_text, parse_mode="HTML", reply_markup=main_menu())
        return

    if data == "binance_sell_option":
        bot.answer_callback_query(call.id)
        
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            print(e)
            
        user_state[user_id] = {"step": "waiting_amount"}
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬅️ 𝗕𝗔𝗖𝗞", callback_data="back_to_main_menu"))

        amount_msg = (
            f"{E_MONEY} 𝗘𝗡𝗧𝗘𝗥 𝗔𝗠𝗢𝗨𝗡𝗧 (𝗨𝗦𝗗)\n\n"
            f"{E_CHART} 𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗥𝗔𝗧𝗘: 1 𝗨𝗦𝗗 = {DOLAR_RATE} 𝗕𝗗𝗧\n\n"
            f"{E_POINT} 𝗣𝗟𝗘𝗔𝗦𝗘 𝗘𝗡𝗧𝗘𝗥 𝗧𝗛𝗘 𝗧𝗢𝗧𝗔𝗟 𝗗𝗢𝗟𝗟𝗔𝗥𝗦 𝗬𝗢𝗨 𝗪𝗜𝗦𝗛 𝗧𝗢 𝗦𝗘𝗟𝗟:"
        )
        sent_msg = bot.send_message(user_id, amount_msg, parse_mode="HTML", reply_markup=markup)
        user_state[user_id]["amount_msg_id"] = sent_msg.message_id
        return

    if data == "atm_bkash":
        bot.answer_callback_query(call.id)
        try:
            prev_msg_id = user_state.get(user_id, {}).get("bkash_prompt_msg_id")
            if prev_msg_id:
                bot.delete_message(call.message.chat.id, prev_msg_id)
        except Exception:
            pass
            
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬅ 𝗕𝗔𝗖𝗞", callback_data="back_to_main_menu"))
        bot.send_message(user_id, f"{E_PHONE} 𝗣𝗟𝗘𝗔𝗦𝗘 𝗘𝗡𝗧𝗘𝗥 𝗬𝗢𝗨𝗥 𝗕𝗞𝗔𝗦𝗛 𝗡𝗨𝗠𝗕𝗘𝗥:", parse_mode="HTML", reply_markup=markup)
        return

    if data in ["dummy_tx", "dummy_sc"]:
        bot.answer_callback_query(call.id)
        return

    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ 𝗣𝗘𝗥𝗠𝗜𝗦𝗦𝗜𝗢𝗡 𝗗𝗘𝗡𝗜𝗘𝗗!", show_alert=True)
        return

    if data.startswith("app_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "Order approved!")
        
        success_msg = (
            f"━━━━━━━━━━━━━\n"
            f"{E_CHECK} 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟\n"
            f"━━━━━━━━━━━━━\n"
            f"💸 𝗥𝗘𝗤𝗨𝗘𝗦𝗧𝗘𝗗 𝗙𝗨𝗡𝗗𝗦 𝗛𝗔𝗩𝗘 𝗕𝗘𝗘𝗡 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬 𝗦𝗘𝗡𝗧 𝗧𝗢 𝗬𝗢𝗨𝗥 𝗣𝗥𝗢𝗩𝗜𝗗𝗘𝗗 𝗡𝗨𝗠𝗕𝗘𝗥.\n"
            f"━━━━━━━━━━━━━"
        )
        bot.send_message(target_user, success_msg, parse_mode="HTML", reply_markup=main_menu())
        
        try:
            bot.edit_message_caption(caption=call.message.caption + f"\n\n{E_CHECK} 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 & 𝗣𝗔𝗜𝗗", parse_mode="HTML", chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception:
            bot.edit_message_text(text=call.message.text + f"\n\n{E_CHECK} 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 & 𝗣𝗔𝗜𝗗", parse_mode="HTML", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data.startswith("rej_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "Order rejected.")
        
        reject_msg = (
            f"━━━━━━━━━━━━━\n"
            f"{E_CROSS} 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗥𝗘𝗝𝗘𝗖𝗧𝗘𝗗\n"
            f"━━━━━━━━━━━━━\n"
            f"{E_WARNING} 𝗬𝗢𝗨𝗥 𝗢𝗥𝗗𝗘𝗥 𝗪𝗔𝗦 𝗥𝗘𝗝𝗘𝗖𝗧𝗘𝗗. 𝗣𝗟𝗘𝗔𝗦𝗘 𝗖𝗢𝗡𝗧𝗔𝗖𝗧 𝗦𝗨𝗣𝗣𝗢𝗥𝗧.\n"
            f"━━━━━━━━━━━━━"
        )
        bot.send_message(target_user, reject_msg, parse_mode="HTML", reply_markup=main_menu())
        
        try:
            bot.edit_message_caption(caption=call.message.caption + f"\n\n{E_CROSS} 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗥𝗘𝗝𝗘𝗖𝗧𝗘𝗗", parse_mode="HTML", chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception:
            bot.edit_message_text(text=call.message.text + f"\n\n{E_CROSS} 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗥𝗘𝗝𝗘𝗖𝗧𝗘𝗗", parse_mode="HTML", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data == "admin_toggle":
        bot_status["is_active"] = not bot_status["is_active"]
        status_text = "𝗔𝗖𝗧𝗜𝗩𝗘" if bot_status["is_active"] else "𝗢𝗙𝗙"
        bot.answer_callback_query(call.id, f"𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗨𝗦: {status_text}", show_alert=True)

    elif data == "admin_broadcast":
        user_state[ADMIN_ID] = {"step": "waiting_broadcast"}
        bot.send_message(ADMIN_ID, f"📢 𝗣𝗟𝗘𝗔𝗦𝗘 𝗘𝗡𝗧𝗘𝗥 𝗬𝗢𝗨𝗥 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗠𝗘𝗦𝗦𝗔𝗚𝗘:", parse_mode="HTML")

if __name__ == "__main__":
    print("Bot is starting on Railway...")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
