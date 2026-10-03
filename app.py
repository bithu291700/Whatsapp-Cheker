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

# Custom Emoji IDs (Telegram Premium Custom Emojis)
EMOJI_CHECK = "5206607081334906820"     # 1) ✅
EMOJI_LIGHTNING = "5456140674028019486" # 2) ⚡
EMOJI_BAN = "5240241223632954241"       # 3) 🚫
EMOJI_SHIELD = "5416081784641168838"    # 4) 🛡️
EMOJI_DOLLAR = "5409048419211682843"    # 5) 💵
EMOJI_BADGE = "5397916757333654639"     # 6) 🔰
EMOJI_DIAMOND = "5427168083074628963"   # 7) 💎
EMOJI_GLOBE = "5386367538735104399"     # 8) 🌐
EMOJI_CHART = "5244837092042750681"     # 9) 📈
EMOJI_PHONE = "5337010556253543833"     # 10) 📞
EMOJI_PLANE = "5323628709469495421"     # 11) ✈️

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_sell = types.KeyboardButton(f"💵 𝗦𝗘𝗟𝗟 𝗗𝗢𝗟𝗟𝗘𝗥")
    btn_support = types.KeyboardButton(f"📞 𝗦𝗨𝗣𝗣𝗢𝗥𝗧")
    btn_admin = types.KeyboardButton(f"👑 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟")
    markup.add(btn_sell, btn_support, btn_admin)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not bot_status["is_active"] and message.from_user.id != ADMIN_ID:
        bot.reply_to(message, f"⚠️ <tg-emoji emoji-id='{EMOJI_BAN}'>🚫</tg-emoji> <b>𝗗𝗨𝗞𝗞𝗛𝗜𝗧𝗢! 𝗕𝗢𝗥𝗧𝗢𝗠𝗔𝗡𝗘 𝗔𝗠𝗔𝗗𝗘𝗥 𝗦𝗘𝗥𝗩𝗜𝗖𝗘 𝗕𝗢𝗡𝗗𝗛𝗢 𝗥𝗢𝗬𝗘𝗖𝗛𝗘.</b>", parse_mode="HTML")
        return
    
    user_state.pop(message.from_user.id, None)
    welcome_text = (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤲 <b>𝗔𝗦𝗦𝗔𝗟𝗔𝗠𝗨 𝗔𝗟𝗔𝗜𝗞𝗨𝗠</b> <tg-emoji emoji-id='{EMOJI_CHECK}'>✅</tg-emoji>\n"
        f"👤 <b>𝗜'𝗠 𝗦𝗔𝗜𝗠</b>\n"
        f"👑 <b>𝗔𝗗𝗠𝗜𝗡 𝗢𝗙 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧</b> <tg-emoji emoji-id='{EMOJI_SHIELD}'>🛡️</tg-emoji>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🌟 <b>𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧 𝗭𝗢𝗡𝗘!</b> <tg-emoji emoji-id='{EMOJI_DIAMOND}'>💎</tg-emoji>\n"
        f"💱 <b>𝗥𝗔𝗧𝗘:</b> 1 𝗨𝗦𝗗 = {DOLAR_RATE} 𝗕𝗗𝗧 <tg-emoji emoji-id='{EMOJI_DOLLAR}'>💵</tg-emoji>\n\n"
        f"👇 <b>𝗣𝗟𝗘𝗔𝗦𝗘 𝗦𝗘𝗟𝗘𝗖𝗧 𝗔𝗡 𝗢𝗣𝗧𝗜𝗢𝗡:</b>"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="HTML", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text

    if not bot_status["is_active"] and user_id != ADMIN_ID:
        bot.reply_to(message, f"⚠️ <tg-emoji emoji-id='{EMOJI_BAN}'>🚫</tg-emoji> <b>𝗕𝗢𝗧-𝗧𝗜 𝗕𝗢𝗥𝗧𝗢𝗠𝗔𝗡𝗘 𝗢𝗙𝗙𝗟𝗜𝗡𝗘 𝗥𝗢𝗬𝗘𝗖𝗛𝗘.</b>", parse_mode="HTML")
        return

    if "𝗦𝗘𝗟𝗟 𝗗𝗢𝗟𝗟𝗘𝗥" in text:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("𝗕𝗜𝗡𝗔𝗡𝗖𝗘", callback_data="binance_sell_option"))
        markup.add(types.InlineKeyboardButton("⬅️ 𝗕𝗔𝗖𝗞", callback_data="back_to_main_menu"))
        
        msg = (
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤲 <b>𝗔𝗦𝗦𝗔𝗟𝗔𝗠𝗨 𝗔𝗟𝗔𝗜𝗞𝗨𝗠</b> <tg-emoji emoji-id='{EMOJI_CHECK}'>✅</tg-emoji>\n"
            f"👤 <b>𝗜'𝗠 𝗦𝗔𝗜𝗠</b>\n"
            f"👑 <b>𝗔𝗗𝗠𝗜𝗡 𝗢𝗙 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧</b> <tg-emoji emoji-id='{EMOJI_SHIELD}'>🛡️</tg-emoji>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📈 <b>𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗥𝗔𝗧𝗘:</b> {DOLAR_RATE} 𝗕𝗗𝗧 / 𝗨𝗦𝗗 <tg-emoji emoji-id='{EMOJI_CHART}'>📈</tg-emoji>\n\n"
            f"👇 <b>𝗖𝗟𝗜𝗖𝗞 𝗧𝗛𝗘 𝗕𝗨𝗧𝗧𝗢𝗡 𝗕𝗘𝗟𝗢𝗪:</b>"
        )
        remove_markup = types.ReplyKeyboardRemove()
        bot.send_message(user_id, "Menu hidden", reply_markup=remove_markup)
        bot.send_message(user_id, msg, parse_mode="HTML", reply_markup=markup)

    elif "𝗦𝗨𝗣𝗣𝗢𝗥𝗧" in text:
        user_state.pop(user_id, None)
        support_msg = (
            f"🛠 <tg-emoji emoji-id='{EMOJI_PHONE}'>📞</tg-emoji> <b>𝗖𝗨𝗦𝗧𝗢𝗠𝗘𝗥 𝗦𝗨𝗣𝗣𝗢𝗥𝗧 & 𝗛𝗘𝗟𝗣 𝗗𝗘𝗦𝗞</b>\n\n"
            f"𝗔𝗗𝗠𝗜𝗡 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘: @{ADMIN_USERNAME}"
        )
        bot.send_message(user_id, support_msg, parse_mode="HTML", reply_markup=main_menu())

    elif "𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟" in text:
        if user_id != ADMIN_ID:
            bot.send_message(user_id, f"❌ <tg-emoji emoji-id='{EMOJI_BAN}'>🚫</tg-emoji> <b>𝗣𝗘𝗥𝗠𝗜𝗦𝗦𝗜𝗢𝗡 𝗗𝗘𝗡𝗜𝗘𝗗!</b>\n\n𝗨𝗦𝗘𝗥 𝗜𝗗: {user_id}", parse_mode="HTML", reply_markup=main_menu())
            return
        
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("📢 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧", callback_data="admin_broadcast"),
            types.InlineKeyboardButton("💱 𝗥𝗔𝗧𝗘 𝗖𝗛𝗔𝗡𝗚𝗘", callback_data="admin_rate"),
            types.InlineKeyboardButton("🔄 𝗕𝗢𝗧 𝗢𝗡/𝗢𝗙𝗙", callback_data="admin_toggle")
        )
        bot.send_message(user_id, f"👑 <tg-emoji emoji-id='{EMOJI_BADGE}'>🔰</tg-emoji> <b>𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗡𝗧𝗥𝗢𝗟 𝗣𝗔𝗡𝗘𝗟</b>", parse_mode="HTML", reply_markup=admin_markup)

    elif user_state.get(user_id, {}).get("step") == "waiting_broadcast":
        if user_id == ADMIN_ID:
            user_state.pop(user_id, None)
            bot.send_message(user_id, f"✅ <tg-emoji emoji-id='{EMOJI_CHECK}'>✅</tg-emoji> <b>𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗦𝗘𝗡𝗧!</b>\n\n{text}", parse_mode="HTML", reply_markup=main_menu())

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
            markup.add(types.InlineKeyboardButton("⬅️ 𝗕𝗔𝗖𝗞", callback_data="back_to_main_menu"))

            binance_msg = (
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🤲 <b>𝗔𝗦𝗦𝗔𝗟𝗔𝗠𝗨 𝗔𝗟𝗔𝗜𝗞𝗨𝗠</b> <tg-emoji emoji-id='{EMOJI_CHECK}'>✅</tg-emoji>\n"
                f"👤 <b>𝗜'𝗠 𝗦𝗔𝗜𝗠</b>\n"
                f"👑 <b>𝗔𝗗𝗠𝗜𝗡 𝗢𝗙 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧</b> <tg-emoji emoji-id='{EMOJI_SHIELD}'>🛡️</tg-emoji>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"✅ <b>𝗦𝗘𝗟𝗟𝗜𝗡𝗚:</b> {amount} 𝗨𝗦𝗗 <tg-emoji emoji-id='{EMOJI_DOLLAR}'>💵</tg-emoji>\n"
                f"💰 <b>𝗬𝗢𝗨 𝗪𝗜𝗟𝗟 𝗚𝗘𝗧:</b> {total_taka} 𝗕𝗗𝗧\n\n"
                f"💎 <b>𝗕𝗜𝗡𝗔𝗡𝗖𝗘 𝗣𝗔𝗬 𝗜𝗗:</b>\n`{BINANCE_ID}`\n\n"
                f"📥 <b>𝗣𝗟𝗘𝗔𝗦𝗘 𝗘𝗡𝗧𝗘𝗥 𝗬𝗢𝗨𝗥 𝗢𝗥𝗗𝗘𝗥 𝗜𝗗 (𝗧𝗫𝗜𝗗):</b>"
            )
            sent_msg = bot.send_message(user_id, binance_msg, parse_mode="Markdown", reply_markup=markup)
            user_state[user_id]["binance_msg_id"] = sent_msg.message_id
        except ValueError:
            bot.send_message(user_id, f"⚠️ <tg-emoji emoji-id='{EMOJI_BAN}'>🚫</tg-emoji> <b>𝗣𝗟𝗘𝗔𝗦𝗘 𝗘𝗡𝗧𝗘𝗥 𝗔 𝗩𝗔𝗟𝗜𝗗 𝗡𝗨𝗠𝗕𝗘𝗥!</b>", parse_mode="HTML")

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
            f"✅ <tg-emoji emoji-id='{EMOJI_CHECK}'>✅</tg-emoji> <b>𝗧𝗥𝗔𝗡𝗦𝗔𝗖𝗧𝗜𝗢𝗡 𝗜𝗗 𝗥𝗘𝗖𝗘𝗜𝗩𝗘𝗗!</b>\n"
            f"━━━━━━━━━━━━━\n\n"
            f"📸 <b>𝗡𝗢𝗪 𝗣𝗟𝗘𝗔𝗦𝗘 𝗨𝗣𝗟𝗢𝗔𝗗 𝗧𝗛𝗘 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗦𝗖𝗥𝗘𝗘𝗡𝗦𝗛𝗢𝗧</b> <tg-emoji emoji-id='{EMOJI_PLANE}'>✈️</tg-emoji> 👇", 
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
            f"⏳ <b>𝗥𝗘𝗤𝗨𝗘𝗦𝗧 𝗦𝗨𝗕𝗠𝗜𝗧𝗧𝗘𝗗</b> <tg-emoji emoji-id='{EMOJI_GLOBE}'>🌐</tg-emoji>\n"
            f"━━━━━━━━━━━━━\n"
            f"✅ <b>𝗣𝗟𝗘𝗔𝗦𝗘 𝗦𝗧𝗔𝗬 𝗢𝗡𝗟𝗜𝗡𝗘. 𝗬𝗢𝗨𝗥 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗪𝗜𝗟𝗟 𝗕𝗘 𝗦𝗘𝗡𝗧 𝗧𝗢 𝗬𝗢𝗨𝗥 𝗔𝗖𝗖𝗢𝗨𝗡𝗧 𝗦𝗛𝗢𝗥𝗧𝗟𝗬 𝗪𝗜𝗧𝗛𝗜𝗡 𝗔 𝗙𝗘𝗪 𝗠𝗜𝗡𝗨𝗧𝗘𝗦.</b>\n"
            f"━━━━━━━━━━━━━\n\n"
            f"┏━━━━━━━ 🌙 ━━━━━━━┓\n"
            f"🤲 <b>𝗔𝗦𝗦𝗔𝗟𝗔𝗠𝗨 𝗔𝗟𝗔𝗜𝗞𝗨𝗠</b> <tg-emoji emoji-id='{EMOJI_CHECK}'>✅</tg-emoji>\n"
            f"👤 <b>𝗜'𝗠 𝗦𝗔𝗜𝗠</b>\n"
            f"👑 <b>𝗔𝗗𝗠𝗜𝗡 𝗢𝗙 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧</b> <tg-emoji emoji-id='{EMOJI_SHIELD}'>🛡️</tg-emoji>\n"
            f"┗━━━━━━━ ⚡ <tg-emoji emoji-id='{EMOJI_LIGHTNING}'>⚡</tg-emoji> ━━━━━━━┛"
        )
        bot.send_message(user_id, summary_msg, parse_mode="HTML", reply_markup=main_menu())

        admin_notification = (
            f"🚨 <b>𝗡𝗘𝗪 𝗗𝗢𝗟𝗟𝗔𝗥 𝗦𝗘𝗟𝗟 𝗢𝗥𝗗𝗘𝗥!</b> <tg-emoji emoji-id='{EMOJI_DIAMOND}'>💎</tg-emoji> 🚨\n\n"
            f"👤 <b>𝗨𝗦𝗘𝗥 𝗜𝗗:</b> {user_id}\n"
            f"💵 <b>𝗗𝗢𝗟𝗟𝗔𝗥:</b> {data['amount']} 𝗨𝗦𝗗\n"
            f"💱 <b>𝗧𝗔𝗞𝗔:</b> {data['total_taka']} 𝗕𝗗𝗧 <tg-emoji emoji-id='{EMOJI_DOLLAR}'>💵</tg-emoji>\n"
            f"🆔 <b>𝗢𝗥𝗗𝗘𝗥 𝗜𝗗:</b> {data['order_id']}\n"
            f"📱 <b>𝗕𝗞𝗔𝗦𝗛:</b> {data['bkash_number']}"
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
            f"✅ <tg-emoji emoji-id='{EMOJI_CHECK}'>✅</tg-emoji> <b>𝗦𝗖𝗥𝗘𝗘𝗡𝗦𝗛𝗢𝗧 𝗥𝗘𝗖𝗘𝗜𝗩𝗘𝗗!</b>\n"
            f"━━━━━━━━━━━━━\n"
            f"🏦 <b>𝗥𝗘𝗖𝗘𝗜𝗩𝗘 𝗠𝗢𝗡𝗘𝗬 𝗩𝗜𝗔</b> <tg-emoji emoji-id='{EMOJI_DOLLAR}'>💵</tg-emoji>\n"
            f"━━━━━━━━━━━━━\n"
            f"👇 <b>𝗦𝗘𝗟𝗘𝗖𝗧 𝗪𝗛𝗘𝗥𝗘 𝗬𝗢𝗨 𝗪𝗔𝗡𝗧 𝗧𝗢 𝗥𝗘𝗖𝗘𝗜𝗩𝗘 𝗬𝗢𝗨𝗥 𝗙𝗨𝗡𝗗𝗦:</b>",
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
            f"🤲 <b>𝗔𝗦𝗦𝗔𝗟𝗔𝗠𝗨 𝗔𝗟𝗔𝗜𝗞𝗨𝗠</b> <tg-emoji emoji-id='{EMOJI_CHECK}'>✅</tg-emoji>\n"
            f"👤 <b>𝗜'𝗠 𝗦𝗔𝗜𝗠</b>\n"
            f"👑 <b>𝗔𝗗𝗠𝗜𝗡 𝗢𝗙 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧</b> <tg-emoji emoji-id='{EMOJI_SHIELD}'>🛡️</tg-emoji>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🌟 <b>𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧 𝗭𝗢𝗡𝗘!</b> <tg-emoji emoji-id='{EMOJI_DIAMOND}'>💎</tg-emoji>\n"
            f"💱 <b>𝗥𝗔𝗧𝗘:</b> 1 𝗨𝗦𝗗 = {DOLAR_RATE} 𝗕𝗗𝗧 <tg-emoji emoji-id='{EMOJI_DOLLAR}'>💵</tg-emoji>\n\n"
            f"👇 <b>𝗣𝗟𝗘𝗔𝗦𝗘 𝗦𝗘𝗟𝗘𝗖𝗧 𝗔𝗡 𝗢𝗣𝗧𝗜𝗢𝗡:</b>"
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
            f"💵 <tg-emoji emoji-id='{EMOJI_DOLLAR}'>💵</tg-emoji> <b>𝗘𝗡𝗧𝗘𝗥 𝗔𝗠𝗢𝗨𝗡𝗧 (𝗨𝗦𝗗)</b>\n\n"
            f"💹 <b>𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗥𝗔𝗧𝗘:</b> 1 𝗨𝗦𝗗 = {DOLAR_RATE} 𝗕𝗗𝗧 <tg-emoji emoji-id='{EMOJI_CHART}'>📈</tg-emoji>\n\n"
            f"👇 <b>𝗣𝗟𝗘𝗔𝗦𝗘 𝗘𝗡𝗧𝗘𝗥 𝗧𝗛𝗘 𝗧𝗢𝗧𝗔𝗟 𝗗𝗢𝗟𝗟𝗔𝗥𝗦 𝗬𝗢𝗨 𝗪𝗜𝗦𝗛 𝗧𝗢 𝗦𝗘𝗟𝗟:</b>"
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
        markup.add(types.InlineKeyboardButton("⬅️ 𝗕𝗔𝗖𝗞", callback_data="back_to_main_menu"))
        bot.send_message(user_id, f"📱 <tg-emoji emoji-id='{EMOJI_PHONE}'>📞</tg-emoji> <b>𝗣𝗟𝗘𝗔𝗦𝗘 𝗘𝗡𝗧𝗘𝗥 𝗬𝗢𝗨𝗥 𝗕𝗞𝗔𝗦𝗛 𝗡𝗨𝗠𝗕𝗘𝗥:</b>", parse_mode="HTML", reply_markup=markup)
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
            f"✅ <tg-emoji emoji-id='{EMOJI_CHECK}'>✅</tg-emoji> <b>𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟</b>\n"
            f"━━━━━━━━━━━━━\n"
            f"💸 <b>𝗥𝗘𝗤𝗨𝗘𝗦𝗧𝗘𝗗 𝗙𝗨𝗡𝗗𝗦 𝗛𝗔𝗩𝗘 𝗕𝗘𝗘𝗡 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬 𝗦𝗘𝗡𝗧 𝗧𝗢 𝗬𝗢𝗨𝗥 𝗣𝗥𝗢𝗩𝗜𝗗𝗘𝗗 𝗡𝗨𝗠𝗕𝗘𝗥.</b> <tg-emoji emoji-id='{EMOJI_LIGHTNING}'>⚡</tg-emoji>\n"
            f"━━━━━━━━━━━━━"
        )
        bot.send_message(target_user, success_msg, parse_mode="HTML", reply_markup=main_menu())
        
        try:
            bot.edit_message_caption(caption=call.message.caption + "\n\n✅ 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 & 𝗣𝗔𝗜𝗗", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
        except Exception:
            bot.edit_message_text(text=call.message.text + "\n\n✅ 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 & 𝗣𝗔𝗜𝗗", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")

    elif data.startswith("rej_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "Order rejected.")
        
        reject_msg = (
            f"━━━━━━━━━━━━━\n"
            f"❌ <tg-emoji emoji-id='{EMOJI_BAN}'>🚫</tg-emoji> <b>𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗥𝗘𝗝𝗘𝗖𝗧𝗘𝗗</b>\n"
            f"━━━━━━━━━━━━━\n"
            f"⚠️ <b>𝗬𝗢𝗨𝗥 𝗢𝗥𝗗𝗘𝗥 𝗪𝗔𝗦 𝗥𝗘𝗝𝗘𝗖𝗧𝗘𝗗. 𝗣𝗟𝗘𝗔𝗦𝗘 𝗖𝗢𝗡𝗧𝗔𝗖𝗧 𝗦𝗨𝗣𝗣𝗢𝗥𝗧.</b>\n"
            f"━━━━━━━━━━━━━"
        )
        bot.send_message(target_user, reject_msg, parse_mode="HTML", reply_markup=main_menu())
        
        try:
            bot.edit_message_caption(caption=call.message.caption + "\n\n❌ 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗥𝗘𝗝𝗘𝗖𝗧𝗘𝗗", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
        except Exception:
            bot.edit_message_text(text=call.message.text + "\n\n❌ 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗥𝗘𝗝𝗘𝗖𝗧𝗘𝗗", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")

    elif data == "admin_toggle":
        bot_status["is_active"] = not bot_status["is_active"]
        status_text = "𝗔𝗖𝗧𝗜𝗩𝗘" if bot_status["is_active"] else "𝗢𝗙𝗙"
        bot.answer_callback_query(call.id, f"𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗨𝗦: {status_text}", show_alert=True)

    elif data == "admin_rate":
        bot.answer_callback_query(call.id, f"𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗥𝗔𝗧𝗘: {DOLAR_RATE} 𝗕𝗗𝗧", show_alert=True)

    elif data == "admin_broadcast":
        user_state[ADMIN_ID] = {"step": "waiting_broadcast"}
        bot.send_message(ADMIN_ID, f"📢 <tg-emoji emoji-id='{EMOJI_GLOBE}'>🌐</tg-emoji> <b>𝗣𝗟𝗘𝗔𝗦𝗘 𝗘𝗡𝗧𝗘𝗥 𝗬𝗢𝗨𝗥 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗠𝗘𝗦𝗦𝗔𝗚𝗘:</b>", parse_mode="HTML")

if __name__ == "__main__":
    print("Bot is starting on Railway...")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
