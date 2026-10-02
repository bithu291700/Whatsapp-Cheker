import os
import telebot
from telebot import types

# শুধু টেলিগ্রাম টোকেনটি রেলওয়ে ভ্যারিয়েবল থেকে নেওয়া হবে
TOKEN = os.environ.get('BOT_TOKEN')

# আপনার আসল টেলিগ্রাম আইডি এখানে দিন (যেমন: 7388500439)
ADMIN_ID = 7388500439          
BINANCE_ID = "123456789"       # আপনার বাইন্যান্স পে আইডি এখানে দিন
ADMIN_USERNAME = "SAIM_X9"     # আপনার ইউজারনেম
DOLAR_RATE = 119.0             # বর্তমান ডলার রেট

bot = telebot.TeleBot(TOKEN)

user_state = {}
bot_status = {"is_active": True}

# প্রধান মেনু (Reply Keyboard)
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
        bot.reply_to(message, "⚠️ দুঃখিত! বর্তমানে আমাদের সার্ভিস সাময়িকভাবে বন্ধ রয়েছে।")
        return
    
    user_state.pop(message.from_user.id, None)
    welcome_text = (
        f"🌟 প্রিমিয়াম ডলার এক্সচেঞ্জ জোনে আপনাকে স্বাগতম! 🌟\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💱 বর্তমান রেট: ১ USD = {DOLAR_RATE} টাকা\n"
        f"⚡ সেবা: দ্রুত ও সম্পূর্ণ নিরাপদ লেনদেন।\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👇 আপনার প্রয়োজনীয় অপশনটি নিচ থেকে সিলেক্ট করুন:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text

    if not bot_status["is_active"] and user_id != ADMIN_ID:
        bot.reply_to(message, "⚠️ বটটি বর্তমানে অফলাইন রয়েছে।")
        return

    if text == "💵 ডলার সেল করুন":
        user_state[user_id] = {"step": "waiting_amount"}
        msg = (
            f"🎉 অভিনন্দন! আপনি আমাদের সাথে সফলভাবে ডলার সেল করা শুরু করেছেন।\n\n"
            f"📈 বর্তমান এক্সচেঞ্জ রেট: {DOLAR_RATE} টাকা / USD\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✏️ আপনি কত ডলার (USD) সেল করতে চান?\n"
            f"দয়া করে শুধু সংখ্যাটি (যেমন: 10 বা 50) নিচে লিখে পাঠান:"
        )
        bot.send_message(user_id, msg, reply_markup=main_menu())

    elif text == "📞 হেল্প ও সাপোর্ট":
        user_state.pop(user_id, None)
        support_msg = (
            f"🛠 কাস্টমার সাপোর্ট ও হেল্প ডেস্ক\n\n"
            f"যেকোনো প্রয়োজনে আমাদের অফিশিয়াল অ্যাডমিনের সাথে যোগাযোগ করুন:\n\n"
            f"👤 অ্যাডমিন ইউজারনেম: @{ADMIN_USERNAME}"
        )
        bot.send_message(user_id, support_msg, reply_markup=main_menu())

    elif text == "👑 অ্যাডমিন প্যানেল":
        if user_id != ADMIN_ID:
            bot.send_message(user_id, f"❌ আপনার এই প্যানেল ব্যবহার করার অনুমতি নেই!\n\nআপনার টেলিগ্রাম ইউজার আইডি: {user_id}", reply_markup=main_menu())
            return
        
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("📢 ব্রডকাস্ট", callback_data="admin_broadcast"),
            types.InlineKeyboardButton("💱 রেট পরিবর্তন", callback_data="admin_rate"),
            types.InlineKeyboardButton("🔄 বট অন/অফ", callback_data="admin_toggle")
        )
        bot.send_message(user_id, "👑 অ্যাডমিন কন্ট্রোল প্যানেল\n\nনিচের অপশনগুলো থেকে কাজ সিলেক্ট করুন:", reply_markup=admin_markup)

    elif user_state.get(user_id, {}).get("step") == "waiting_broadcast":
        if user_id == ADMIN_ID:
            user_state.pop(user_id, None)
            bot.send_message(user_id, f"✅ ব্রডকাস্ট সফলভাবে সম্পন্ন হয়েছে!\n\nবার্তা:\n{text}", reply_markup=main_menu())

    elif user_state.get(user_id, {}).get("step") == "waiting_amount":
        try:
            amount = float(text)
            total_taka = amount * DOLAR_RATE
            user_state[user_id]["amount"] = amount
            user_state[user_id]["total_taka"] = total_taka
            user_state[user_id]["step"] = "waiting_order_id"

            binance_msg = (
                f"✅ আপনি সেল করতে চাচ্ছেন: {amount} USD\n"
                f"💰 আপনি পাবেন: {total_taka} টাকা\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💎 পেমেন্ট নির্দেশিকা:\n"
                f"দয়া করে নিচের বাইন্যান্স পে আইডিতে ডলার সেন্ড করুন:\n\n"
                f"🆔 বাইন্যান্স পে আইডি: {BINANCE_ID}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📥 ডলার পাঠানোর পর অর্ডার আইডি (TXID) টি এখানে লিখে পাঠান:"
            )
            bot.send_message(user_id, binance_msg, reply_markup=main_menu())
        except ValueError:
            bot.send_message(user_id, "⚠️ দয়া করে সঠিক সংখ্যা লিখুন (যেমন: 10 বা 20)", reply_markup=main_menu())

    elif user_state.get(user_id, {}).get("step") == "waiting_order_id":
        user_state[user_id]["order_id"] = text
        user_state[user_id]["step"] = "waiting_screenshot"
        bot.send_message(user_id, "✅ অর্ডার আইডি গ্রহণ করা হয়েছে!\n\n📸 এখন আপনার বাইন্যান্স পেমেন্টের স্ক্রিনশট ছবি আকারে পাঠান:", reply_markup=main_menu())

    elif user_state.get(user_id, {}).get("step") == "waiting_bkash":
        user_state[user_id]["bkash_number"] = text
        data = user_state[user_id]
        user_state[user_id]["step"] = "completed"

        summary_msg = (
            f"🎉 আপনার অর্ডারটি সফলভাবে সাবমিট হয়েছে!\n\n"
            f"💵 ডলার: {data['amount']} USD\n"
            f"💰 টাকা: {data['total_taka']} BDT\n"
            f"🆔 অর্ডার আইডি: {data['order_id']}\n"
            f"📱 বিকাশ নম্বর: {data['bkash_number']}\n\n"
            f"⏳ ১৫ মিনিট অপেক্ষা করুন। পেমেন্ট সম্পন্ন হলে এসএমএস পাবেন।"
        )
        bot.send_message(user_id, summary_msg, reply_markup=main_menu())

        admin_notification = (
            f"🚨 নতুন ডলার সেল অর্ডার এসেছে! 🚨\n\n"
            f"👤 ইউজার আইডি: {user_id}\n"
            f"💵 ডলার: {data['amount']} USD\n"
            f"💱 টাকা: {data['total_taka']} BDT\n"
            f"🆔 অর্ডার আইডি: {data['order_id']}\n"
            f"📱 বিকাশ নম্বর: {data['bkash_number']}"
        )
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("✅ এপ্রুভ করুন", callback_data=f"app_{user_id}"),
            types.InlineKeyboardButton("❌ বাতিল করুন", callback_data=f"rej_{user_id}")
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
            "✅ স্ক্রিনশট সফলভাবে সংরক্ষিত হয়েছে!\n\n"
            "💳 এখন আপনার যে বিকাশ নম্বরে টাকা নিতে চান তা নিচে লিখে পাঠান:",
            reply_markup=main_menu()
        )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global DOLAR_RATE
    user_id = call.from_user.id
    data = call.data

    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ এই কাজ করার অনুমতি আপনার নেই!", show_alert=True)
        return

    if data.startswith("app_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "অর্ডারটি সফলভাবে এপ্রুভ করা হয়েছে!")
        bot.send_message(
            target_user, 
            "🎉 অভিনন্দন! আপনার ডলার অর্ডারটি ভেরিফাই এবং পেমেন্ট সম্পন্ন হয়েছে।", 
            reply_markup=main_menu()
        )
        try:
            bot.edit_message_caption(caption=call.message.caption + "\n\n✅ স্ট্যাটাস: এপ্রুভড ও পেমেন্ট সম্পন্ন", chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception:
            bot.edit_message_text(text=call.message.text + "\n\n✅ স্ট্যাটাস: এপ্রুভড ও পেমেন্ট সম্পন্ন", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data.startswith("rej_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "অর্ডারটি বাতিল করা হয়েছে।")
        bot.send_message(
            target_user, 
            "⚠️ সতর্কবার্তা! আপনার অর্ডারটি বাতিল করা হয়েছে। সঠিক তথ্য দিয়ে আবার চেষ্টা করুন।", 
            reply_markup=main_menu()
        )
        try:
            bot.edit_message_caption(caption=call.message.caption + "\n\n❌ স্ট্যাটাস: বাতিল করা হয়েছে", chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception:
            bot.edit_message_text(text=call.message.text + "\n\n❌ স্ট্যাটাস: বাতিল করা হয়েছে", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data == "admin_toggle":
        bot_status["is_active"] = not bot_status["is_active"]
        status_text = "চালু" if bot_status["is_active"] else "বন্ধ"
        bot.answer_callback_query(call.id, f"বটের স্ট্যাটাস: {status_text}", show_alert=True)

    elif data == "admin_rate":
        bot.answer_callback_query(call.id, f"বর্তমান রেট: {DOLAR_RATE} টাকা", show_alert=True)

    elif data == "admin_broadcast":
        user_state[ADMIN_ID] = {"step": "waiting_broadcast"}
        bot.send_message(ADMIN_ID, "📢 ব্রডকাস্ট করার মেসেজটি লিখে পাঠান:")

if __name__ == "__main__":
    print("Bot is starting on Railway...")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
