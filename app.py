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

# Custom Emoji IDs (28 Premium Emojis)
E1 = "5397916757333654639"   # 1
E2 = "5253742260054409879"   # 2
E3 = "5217822164362739968"   # 3
E4 = "5424972470023104089"   # 4
E5 = "54607551261312667"     # 5
E6 = "5395695537687123235"   # 6
E7 = "5267500801240092311"   # 7
E8 = "5334759662677957452"   # 8
E9 = "5332600543963522398"   # 9
E10 = "5334863012475986105"  # 10
E11 = "5028746137645876535"  # 11
E12 = "5323628709469495421"  # 12
E13 = "5780463361175066565"  # 13
E14 = "5447410659077661506"  # 14
E15 = "5274099962655816924"  # 15
E16 = "5440660757194744323"  # 16
E17 = "5240241223632954241"  # 17
E18 = "5260293700088511294"  # 18
E19 = "5229064374403998351"  # 19
E20 = "5449683594425410231"  # 20
E21 = "5451882707875276247"  # 21
E22 = "543613877181941026"    # 22
E23 = "5447644880824181073"  # 23
E24 = "5391032818111363540"  # 24
E25 = "5406745015365943482"  # 25
E26 = "5416041192905265756"  # 26
E27 = "5422439311196834318"  # 27
E28 = "5395695537687123235"  # 28

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_sell = types.KeyboardButton(f"SELL DOLLER")
    btn_support = types.KeyboardButton(f"SUPPORT")
    btn_admin = types.KeyboardButton(f"ADMIN PANEL")
    markup.add(btn_sell, btn_support, btn_admin)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not bot_status["is_active"] and message.from_user.id != ADMIN_ID:
        bot.reply_to(message, f"<tg-emoji emoji-id='{E3}'>🚫</tg-emoji> <b>DUKKHITO! BORTOMANE AMADER SERVICE BONDHO ROYЕCHE.</b>", parse_mode="HTML")
        return
    
    user_state.pop(message.from_user.id, None)
    welcome_text = (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"ASSALAMU ALAIKUM <tg-emoji emoji-id='{E1}'>✅</tg-emoji>\n"
        f"I'M SAIM <tg-emoji emoji-id='{E2}'>👤</tg-emoji>\n"
        f"ADMIN OF REX PRIVATE BOT <tg-emoji emoji-id='{E4}'>👑</tg-emoji>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"WELCOME TO REX PRIVATE BOT ZONE! <tg-emoji emoji-id='{E5}'>🌟</tg-emoji>\n"
        f"RATE: 1 USD = {DOLAR_RATE} BDT <tg-emoji emoji-id='{E6}'>💱</tg-emoji>\n\n"
        f"PLEASE SELECT AN OPTION: <tg-emoji emoji-id='{E7}'>👇</tg-emoji>"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="HTML", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text

    if not bot_status["is_active"] and user_id != ADMIN_ID:
        bot.reply_to(message, f"<tg-emoji emoji-id='{E3}'>🚫</tg-emoji> <b>BOT-TI BORTOMANE OFFLINE ROYЕCHE.</b>", parse_mode="HTML")
        return

    if "SELL DOLLER" in text:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("BINANCE", callback_data="binance_sell_option"))
        markup.add(types.InlineKeyboardButton("BACK", callback_data="back_to_main_menu"))
        
        msg = (
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"ASSALAMU ALAIKUM <tg-emoji emoji-id='{E1}'>✅</tg-emoji>\n"
            f"I'M SAIM <tg-emoji emoji-id='{E2}'>👤</tg-emoji>\n"
            f"ADMIN OF REX PRIVATE BOT <tg-emoji emoji-id='{E4}'>👑</tg-emoji>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"CURRENT RATE: {DOLAR_RATE} BDT / USD <tg-emoji emoji-id='{E8}'>📈</tg-emoji>\n\n"
            f"CLICK THE BUTTON BELOW: <tg-emoji emoji-id='{E7}'>👇</tg-emoji>"
        )
        remove_markup = types.ReplyKeyboardRemove()
        bot.send_message(user_id, "Menu hidden", reply_markup=remove_markup)
        bot.send_message(user_id, msg, parse_mode="HTML", reply_markup=markup)

    elif "SUPPORT" in text:
        user_state.pop(user_id, None)
        support_msg = (
            f"CUSTOMER SUPPORT & HELP DESK <tg-emoji emoji-id='{E9}'>📞</tg-emoji>\n\n"
            f"ADMIN USERNAME: @{ADMIN_USERNAME}"
        )
        bot.send_message(user_id, support_msg, parse_mode="HTML", reply_markup=main_menu())

    elif "ADMIN PANEL" in text:
        if user_id != ADMIN_ID:
            bot.send_message(user_id, f"PERMISSION DENIED! <tg-emoji emoji-id='{E3}'>❌</tg-emoji>\n\nUSER ID: {user_id}", parse_mode="HTML", reply_markup=main_menu())
            return
        
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("BROADCAST", callback_data="admin_broadcast"),
            types.InlineKeyboardButton("RATE CHANGE", callback_data="admin_rate"),
            types.InlineKeyboardButton("BOT ON/OFF", callback_data="admin_toggle")
        )
        bot.send_message(user_id, f"ADMIN CONTROL PANEL <tg-emoji emoji-id='{E10}'>👑</tg-emoji>", parse_mode="HTML", reply_markup=admin_markup)

    elif user_state.get(user_id, {}).get("step") == "waiting_broadcast":
        if user_id == ADMIN_ID:
            user_state.pop(user_id, None)
            bot.send_message(user_id, f"BROADCAST SENT! <tg-emoji emoji-id='{E1}'>✅</tg-emoji>\n\n{text}", parse_mode="HTML", reply_markup=main_menu())

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
            markup.add(types.InlineKeyboardButton("BACK", callback_data="back_to_main_menu"))

            binance_msg = (
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"ASSALAMU ALAIKUM <tg-emoji emoji-id='{E1}'>✅</tg-emoji>\n"
                f"I'M SAIM <tg-emoji emoji-id='{E2}'>👤</tg-emoji>\n"
                f"ADMIN OF REX PRIVATE BOT <tg-emoji emoji-id='{E4}'>👑</tg-emoji>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"SELLING: {amount} USD <tg-emoji emoji-id='{E11}'>💵</tg-emoji>\n"
                f"YOU WILL GET: {total_taka} BDT <tg-emoji emoji-id='{E12}'>💰</tg-emoji>\n\n"
                f"BINANCE PAY ID: <tg-emoji emoji-id='{E13}'>💎</tg-emoji>\n`{BINANCE_ID}`\n\n"
                f"PLEASE ENTER YOUR ORDER ID (TXID): <tg-emoji emoji-id='{E7}'>📥</tg-emoji>"
            )
            sent_msg = bot.send_message(user_id, binance_msg, parse_mode="Markdown", reply_markup=markup)
            user_state[user_id]["binance_msg_id"] = sent_msg.message_id
        except ValueError:
            bot.send_message(user_id, f"PLEASE ENTER A VALID NUMBER! <tg-emoji emoji-id='{E3}'>⚠️</tg-emoji>", parse_mode="HTML")

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
            types.InlineKeyboardButton("TRANSACTION ID", callback_data="dummy_tx"),
            types.InlineKeyboardButton("NEXT SCREENSHOT", callback_data="dummy_sc")
        )
        markup.add(types.InlineKeyboardButton("BACK", callback_data="back_to_main_menu"))

        sent_msg = bot.send_message(
            user_id, 
            f"━━━━━━━━━━━━━\n"
            f"TRANSACTION ID RECEIVED! <tg-emoji emoji-id='{E14}'>✅</tg-emoji>\n"
            f"━━━━━━━━━━━━━\n\n"
            f"NOW PLEASE UPLOAD THE PAYMENT SCREENSHOT <tg-emoji emoji-id='{E15}'>📸</tg-emoji> 👇", 
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
            f"REQUEST SUBMITTED <tg-emoji emoji-id='{E16}'>⏳</tg-emoji>\n"
            f"━━━━━━━━━━━━━\n"
            f"PLEASE STAY ONLINE. YOUR PAYMENT WILL BE SENT TO YOUR ACCOUNT SHORTLY WITHIN A FEW MINUTES. <tg-emoji emoji-id='{E17}'>✅</tg-emoji>\n"
            f"━━━━━━━━━━━━━\n\n"
            f"┏━━━━━━━ MOON ━━━━━━━┓\n"
            f"ASSALAMU ALAIKUM <tg-emoji emoji-id='{E1}'>✅</tg-emoji>\n"
            f"I'M SAIM <tg-emoji emoji-id='{E2}'>👤</tg-emoji>\n"
            f"ADMIN OF REX PRIVATE BOT <tg-emoji emoji-id='{E4}'>👑</tg-emoji>\n"
            f"┗━━━━━━━ LIGHT ━━━━━━━┛"
        )
        bot.send_message(user_id, summary_msg, parse_mode="HTML", reply_markup=main_menu())

        admin_notification = (
            f"NEW DOLLAR SELL ORDER! <tg-emoji emoji-id='{E18}'>🚨</tg-emoji>\n\n"
            f"USER ID: {user_id} <tg-emoji emoji-id='{E19}'>👤</tg-emoji>\n"
            f"DOLLAR: {data['amount']} USD <tg-emoji emoji-id='{E11}'>💵</tg-emoji>\n"
            f"TAKA: {data['total_taka']} BDT <tg-emoji emoji-id='{E12}'>💰</tg-emoji>\n"
            f"ORDER ID: {data['order_id']} <tg-emoji emoji-id='{E20}'>🆔</tg-emoji>\n"
            f"BKASH: {data['bkash_number']} <tg-emoji emoji-id='{E21}'>📱</tg-emoji>"
        )
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("APPROVE", callback_data=f"app_{user_id}"),
            types.InlineKeyboardButton("REJECT", callback_data=f"rej_{user_id}")
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
        markup.add(types.InlineKeyboardButton("ATM BKASH", callback_data="atm_bkash"))
        markup.add(types.InlineKeyboardButton("BACK", callback_data="back_to_main_menu"))

        sent_msg = bot.send_message(
            user_id, 
            f"━━━━━━━━━━━━━\n"
            f"SCREENSHOT RECEIVED! <tg-emoji emoji-id='{E22}'>✅</tg-emoji>\n"
            f"━━━━━━━━━━━━━\n"
            f"RECEIVE MONEY VIA <tg-emoji emoji-id='{E23}'>🏦</tg-emoji>\n"
            f"━━━━━━━━━━━━━\n"
            f"SELECT WHERE YOU WANT TO RECEIVE YOUR FUNDS: <tg-emoji emoji-id='{E7}'>👇</tg-emoji>",
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
            f"ASSALAMU ALAIKUM <tg-emoji emoji-id='{E1}'>✅</tg-emoji>\n"
            f"I'M SAIM <tg-emoji emoji-id='{E2}'>👤</tg-emoji>\n"
            f"ADMIN OF REX PRIVATE BOT <tg-emoji emoji-id='{E4}'>👑</tg-emoji>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"WELCOME TO REX PRIVATE BOT ZONE! <tg-emoji emoji-id='{E5}'>🌟</tg-emoji>\n"
            f"RATE: 1 USD = {DOLAR_RATE} BDT <tg-emoji emoji-id='{E6}'>💱</tg-emoji>\n\n"
            f"PLEASE SELECT AN OPTION: <tg-emoji emoji-id='{E7}'>👇</tg-emoji>"
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
        markup.add(types.InlineKeyboardButton("BACK", callback_data="back_to_main_menu"))

        amount_msg = (
            f"ENTER AMOUNT (USD) <tg-emoji emoji-id='{E24}'>💵</tg-emoji>\n\n"
            f"CURRENT RATE: 1 USD = {DOLAR_RATE} BDT <tg-emoji emoji-id='{E8}'>📈</tg-emoji>\n\n"
            f"PLEASE ENTER THE TOTAL DOLLARS YOU WISH TO SELL: <tg-emoji emoji-id='{E7}'>👇</tg-emoji>"
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
        markup.add(types.InlineKeyboardButton("BACK", callback_data="back_to_main_menu"))
        bot.send_message(user_id, f"PLEASE ENTER YOUR BKASH NUMBER: <tg-emoji emoji-id='{E21}'>📱</tg-emoji>", parse_mode="HTML", reply_markup=markup)
        return

    if data in ["dummy_tx", "dummy_sc"]:
        bot.answer_callback_query(call.id)
        return

    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "PERMISSION DENIED!", show_alert=True)
        return

    if data.startswith("app_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "Order approved!")
        
        success_msg = (
            f"━━━━━━━━━━━━━\n"
            f"PAYMENT SUCCESSFUL <tg-emoji emoji-id='{E25}'>✅</tg-emoji>\n"
            f"━━━━━━━━━━━━━\n"
            f"REQUESTED FUNDS HAVE BEEN SUCCESSFULLY SENT TO YOUR PROVIDED NUMBER. <tg-emoji emoji-id='{E26}'>💸</tg-emoji>\n"
            f"━━━━━━━━━━━━━"
        )
        bot.send_message(target_user, success_msg, parse_mode="HTML", reply_markup=main_menu())
        
        try:
            bot.edit_message_caption(caption=call.message.caption + "\n\nSTATUS: APPROVED & PAID <tg-emoji emoji-id='{E25}'>✅</tg-emoji>", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
        except Exception:
            bot.edit_message_text(text=call.message.text + "\n\nSTATUS: APPROVED & PAID <tg-emoji emoji-id='{E25}'>✅</tg-emoji>", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")

    elif data.startswith("rej_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "Order rejected.")
        
        reject_msg = (
            f"━━━━━━━━━━━━━\n"
            f"PAYMENT REJECTED <tg-emoji emoji-id='{E27}'>❌</tg-emoji>\n"
            f"━━━━━━━━━━━━━\n"
            f"YOUR ORDER WAS REJECTED. PLEASE CONTACT SUPPORT. <tg-emoji emoji-id='{E3}'>⚠️️</tg-emoji>\n"
            f"━━━━━━━━━━━━━"
        )
        bot.send_message(target_user, reject_msg, parse_mode="HTML", reply_markup=main_menu())
        
        try:
            bot.edit_message_caption(caption=call.message.caption + "\n\nSTATUS: REJECTED <tg-emoji emoji-id='{E27}'>❌</tg-emoji>", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
        except Exception:
            bot.edit_message_text(text=call.message.text + "\n\nSTATUS: REJECTED <tg-emoji emoji-id='{E27}'>❌</tg-emoji>", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")

    elif data == "admin_toggle":
        bot_status["is_active"] = not bot_status["is_active"]
        status_text = "ACTIVE" if bot_status["is_active"] else "OFF"
        bot.answer_callback_query(call.id, f"BOT STATUS: {status_text}", show_alert=True)

    elif data == "admin_rate":
        bot.answer_callback_query(call.id, f"CURRENT RATE: {DOLAR_RATE} BDT", show_alert=True)

    elif data == "admin_broadcast":
        user_state[ADMIN_ID] = {"step": "waiting_broadcast"}
        bot.send_message(ADMIN_ID, f"PLEASE ENTER YOUR BROADCAST MESSAGE: <tg-emoji emoji-id='{E28}'>📢</tg-emoji>", parse_mode="HTML")

if __name__ == "__main__":
    print("Bot is starting on Railway...")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
