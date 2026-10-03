import os
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart

TOKEN = os.environ.get('BOT_TOKEN')

ADMIN_ID = 7388500439          
BINANCE_ID = "123456789"       
ADMIN_USERNAME = "SAIM_X9"     
DOLAR_RATE = 120.0             

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_state = {}
bot_status = {"is_active": True}

# Custom Emoji IDs
E1 = "5397916757333654639"   
E2 = "5253742260054409879"   
E4 = "5424972470023104089"   
E5 = "5460755126761312667"   
E7 = "5267500801240092311"   
E9 = "5334759662677957452"   
E10 = "5334863012475986105"  
E11 = "5028746137645876535"  
E12 = "5323628709469495421"  
E13 = "5348212415077064131"  
E14 = "5979054952360711289"  
E18 = "5447410659077661506"  
E19 = "5274099962655816924"  
E20 = "5440660757194744323"  
E21 = "5348469219761626211"  
E24 = "5409048419211682843"  
E25 = "5979054952360711289"  
E26 = "5449683594425410231"  
E27 = "5210952531676504517"  
E33 = "5395695537687123235"  
E34 = "5206607081334906820"  
E35 = "5456140674028019486"  
E36 = "5386367538735104399"  
E38 = "6233367447789899509"  

def main_menu():
    # Style gulo thik rekhe raw dict akare keyboard design kora holo jate aiogram error na dey
    keyboard = {
        "keyboard": [
            [
                {"text": "🟢 SELL DOLLER", "style": "success"},
                {"text": "🔵 SUPPORT", "style": "primary"}
            ],
            [
                {"text": "🔴 ADMIN PANEL", "style": "danger"}
            ]
        ],
        "resize_keyboard": True
    }
    return types.ReplyKeyboardMarkup(**keyboard)

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    if not bot_status["is_active"] and message.from_user.id != ADMIN_ID:
        await message.reply(f"<tg-emoji emoji-id='{E33}'>🚫</tg-emoji> <b>DUKKHITO! BORTOMANE AMADER SERVICE BONDHO ROYЕCHE.</b>", parse_mode="HTML")
        return
    
    user_state.pop(message.from_user.id, None)
    welcome_text = (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"ASSALAMU ALAIKUM <tg-emoji emoji-id='{E1}'>✅</tg-emoji>\n"
        f"I'M SAIM <tg-emoji emoji-id='{E2}'>👤</tg-emoji>\n"
        f"ADMIN OF REX PRIVATE BOT <tg-emoji emoji-id='{E4}'>👑</tg-emoji>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"WELCOME TO REX PRIVATE BOT ZONE! <tg-emoji emoji-id='{E5}'>🌟</tg-emoji>\n"
        f"CURRENT RATE: 1 USD = {DOLAR_RATE} BDT <tg-emoji emoji-id='{E38}'>💱</tg-emoji>\n\n"
        f"PLEASE SELECT AN OPTION: <tg-emoji emoji-id='{E7}'>👇</tg-emoji>"
    )
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=main_menu())

@dp.message(F.text)
async def handle_messages(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    if not bot_status["is_active"] and user_id != ADMIN_ID:
        await message.reply(f"<tg-emoji emoji-id='{E33}'>🚫</tg-emoji> <b>BOT-TI BORTOMANE OFFLINE ROYЕCHE.</b>", parse_mode="HTML")
        return

    if "SELL DOLLER" in text:
        builder = types.InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(text="BINANCE", callback_data="binance_sell_option"),
            types.InlineKeyboardButton(text="BACK", callback_data="back_to_main_menu")
        )
        
        msg = (
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"ASSALAMU ALAIKUM <tg-emoji emoji-id='{E1}'>✅</tg-emoji>\n"
            f"I'M SAIM <tg-emoji emoji-id='{E2}'>👤</tg-emoji>\n"
            f"ADMIN OF REX PRIVATE BOT <tg-emoji emoji-id='{E4}'>👑</tg-emoji>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"CURRENT RATE: {DOLAR_RATE} BDT / USD <tg-emoji emoji-id='{E24}'>📈</tg-emoji>\n\n"
            f"CLICK THE BUTTON BELOW: <tg-emoji emoji-id='{E7}'>👇</tg-emoji>"
        )
        await message.answer("Menu hidden", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(msg, parse_mode="HTML", reply_markup=builder.as_markup())

    elif "SUPPORT" in text:
        user_state.pop(user_id, None)
        support_msg = (
            f"CUSTOMER SUPPORT & HELP DESK <tg-emoji emoji-id='{E9}'>📞</tg-emoji>\n\n"
            f"ADMIN USERNAME: @{ADMIN_USERNAME}"
        )
        await message.answer(support_msg, parse_mode="HTML", reply_markup=main_menu())

    elif "ADMIN PANEL" in text:
        if user_id != ADMIN_ID:
            await message.answer(f"PERMISSION DENIED! <tg-emoji emoji-id='{E34}'>❌</tg-emoji>\n\nUSER ID: {user_id}", parse_mode="HTML", reply_markup=main_menu())
            return
        
        builder = types.InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(text="BROADCAST", callback_data="admin_broadcast"),
            types.InlineKeyboardButton(text="RATE CHANGE", callback_data="admin_rate")
        )
        builder.row(
            types.InlineKeyboardButton(text="BOT ON/OFF", callback_data="admin_toggle")
        )
        await message.answer(f"ADMIN CONTROL PANEL <tg-emoji emoji-id='{E10}'>👑</tg-emoji>", parse_mode="HTML", reply_markup=builder.as_markup())

    elif user_state.get(user_id, {}).get("step") == "waiting_broadcast":
        if user_id == ADMIN_ID:
            user_state.pop(user_id, None)
            await message.answer(f"BROADCAST SENT! <tg-emoji emoji-id='{E14}'>✅</tg-emoji>\n\n{text}", parse_mode="HTML", reply_markup=main_menu())

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
                    await bot.delete_message(user_id, prev_msg_id)
            except Exception:
                pass

            try:
                await message.delete()
            except Exception:
                pass

            builder = types.InlineKeyboardBuilder()
            builder.row(types.InlineKeyboardButton(text="BACK", callback_data="back_to_main_menu"))

            binance_msg = (
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"ASSALAMU ALAIKUM <tg-emoji emoji-id='{E1}'>✅</tg-emoji>\n"
                f"I'M SAIM <tg-emoji emoji-id='{E2}'>👤</tg-emoji>\n"
                f"ADMIN OF REX PRIVATE BOT <tg-emoji emoji-id='{E4}'>👑</tg-emoji>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"SELLING: {amount} USD <tg-emoji emoji-id='{E11}'>💵</tg-emoji>\n"
                f"YOU WILL GET: {total_taka} BDT <tg-emoji emoji-id='{E12}'>💰</tg-emoji>\n\n"
                f"BINANCE PAY ID: <tg-emoji emoji-id='{E13}'>💎</tg-emoji>\n<code>{BINANCE_ID}</code>\n\n"
                f"PLEASE ENTER YOUR ORDER ID (TXID): <tg-emoji emoji-id='{E7}'>📥</tg-emoji>"
            )
            sent_msg = await bot.send_message(user_id, binance_msg, parse_mode="HTML", reply_markup=builder.as_markup())
            user_state[user_id]["binance_msg_id"] = sent_msg.message_id
        except ValueError:
            await message.answer(f"PLEASE ENTER A VALID NUMBER! <tg-emoji emoji-id='{E35}'>⚠️</tg-emoji>", parse_mode="HTML")

    elif user_state.get(user_id, {}).get("step") == "waiting_order_id":
        user_state[user_id]["order_id"] = text
        user_state[user_id]["step"] = "waiting_screenshot"
        
        try:
            prev_msg_id = user_state[user_id].get("binance_msg_id")
            if prev_msg_id:
                await bot.delete_message(user_id, prev_msg_id)
        except Exception:
            pass

        try:
            await message.delete()
        except Exception:
            pass

        builder = types.InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(text="TRANSACTION ID", callback_data="dummy_tx"),
            types.InlineKeyboardButton(text="NEXT SCREENSHOT", callback_data="dummy_sc")
        )
        builder.row(types.InlineKeyboardButton(text="BACK", callback_data="back_to_main_menu"))

        sent_msg = await bot.send_message(
            user_id, 
            f"━━━━━━━━━━━━━\n"
            f"TRANSACTION ID RECEIVED! <tg-emoji emoji-id='{E14}'>✅</tg-emoji>\n"
            f"━━━━━━━━━━━━━\n\n"
            f"NOW PLEASE UPLOAD THE PAYMENT SCREENSHOT <tg-emoji emoji-id='{E7}'>📸</tg-emoji> 👇", 
            parse_mode="HTML",
            reply_markup=builder.as_markup()
        )
        user_state[user_id]["tx_received_msg_id"] = sent_msg.message_id

    elif user_state.get(user_id, {}).get("step") == "waiting_bkash":
        user_state[user_id]["bkash_number"] = text
        data = user_state[user_id]
        user_state[user_id]["step"] = "completed"

        try:
            await message.delete()
        except Exception:
            pass

        summary_msg = (
            f"━━━━━━━━━━━━━\n"
            f"REQUEST SUBMITTED <tg-emoji emoji-id='{E14}'>⏳</tg-emoji>\n"
            f"━━━━━━━━━━━━━\n"
            f"PLEASE STAY ONLINE. YOUR PAYMENT WILL BE SENT TO YOUR ACCOUNT SHORTLY WITHIN A FEW MINUTES. <tg-emoji emoji-id='{E36}'>✅</tg-emoji>\n"
            f"━━━━━━━━━━━━━\n\n"
            f"┏━━━━━━━ MOON ━━━━━━━┓\n"
            f"ASSALAMU ALAIKUM <tg-emoji emoji-id='{E1}'>✅</tg-emoji>\n"
            f"I'M SAIM <tg-emoji emoji-id='{E2}'>👤</tg-emoji>\n"
            f"ADMIN OF REX PRIVATE BOT <tg-emoji emoji-id='{E4}'>👑</tg-emoji>\n"
            f"┗━━━━━━━ LIGHT ━━━━━━━┛"
        )
        await bot.send_message(user_id, summary_msg, parse_mode="HTML", reply_markup=main_menu())

        admin_notification = (
            f"NEW DOLLAR SELL ORDER! <tg-emoji emoji-id='{E18}'>🚨</tg-emoji>\n\n"
            f"USER ID: {user_id} <tg-emoji emoji-id='{E19}'>👤</tg-emoji>\n"
            f"DOLLAR: {data['amount']} USD <tg-emoji emoji-id='{E11}'>💵</tg-emoji>\n"
            f"TAKA: {data['total_taka']} BDT <tg-emoji emoji-id='{E12}'>💰</tg-emoji>\n"
            f"ORDER ID: {data['order_id']} <tg-emoji emoji-id='{E20}'>🆔</tg-emoji>\n"
            f"BKASH: {data['bkash_number']} <tg-emoji emoji-id='{E21}'>📱</tg-emoji>"
        )
        builder = types.InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(text="APPROVE", callback_data=f"app_{user_id}"),
            types.InlineKeyboardButton(text="REJECT", callback_data=f"rej_{user_id}")
        )
        
        if data.get("photo_file_id"):
            await bot.send_photo(ADMIN_ID, data["photo_file_id"], caption=admin_notification, parse_mode="HTML", reply_markup=builder.as_markup())
        else:
            await bot.send_message(ADMIN_ID, admin_notification, parse_mode="HTML", reply_markup=builder.as_markup())

@dp.message(F.photo)
async def handle_photos(message: types.Message):
    user_id = message.from_user.id
    if user_state.get(user_id, {}).get("step") == "waiting_screenshot":
        user_state[user_id]["photo_file_id"] = message.photo[-1].file_id
        user_state[user_id]["step"] = "waiting_bkash"
        
        try:
            prev_msg_id = user_state[user_id].get("tx_received_msg_id")
            if prev_msg_id:
                await bot.delete_message(user_id, prev_msg_id)
        except Exception:
            pass
        
        builder = types.InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="ATM BKASH", callback_data="atm_bkash"))
        builder.row(types.InlineKeyboardButton(text="BACK", callback_data="back_to_main_menu"))

        sent_msg = await bot.send_message(
            user_id, 
            f"━━━━━━━━━━━━━\n"
            f"SCREENSHOT RECEIVED! <tg-emoji emoji-id='{E14}'>✅</tg-emoji>\n"
            f"━━━━━━━━━━━━━\n"
            f"RECEIVE MONEY VIA <tg-emoji emoji-id='{E21}'>🏦</tg-emoji>\n"
            f"━━━━━━━━━━━━━\n"
            f"SELECT WHERE YOU WANT TO RECEIVE YOUR FUNDS: <tg-emoji emoji-id='{E7}'>👇</tg-emoji>",
            parse_mode="HTML",
            reply_markup=builder.as_markup()
        )
        user_state[user_id]["bkash_prompt_msg_id"] = sent_msg.message_id

@dp.callback_query()
async def callback_query(call: types.CallbackQuery):
    global DOLAR_RATE
    user_id = call.from_user.id
    data = call.data

    if data == "back_to_main_menu":
        await call.answer("Returned to Main Menu")
        user_state.pop(user_id, None)
        try:
            await call.message.delete()
        except Exception:
            pass
        
        welcome_text = (
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"ASSALAMU ALAIKUM <tg-emoji emoji-id='{E1}'>✅</tg-emoji>\n"
            f"I'M SAIM <tg-emoji emoji-id='{E2}'>👤</tg-emoji>\n"
            f"ADMIN OF REX PRIVATE BOT <tg-emoji emoji-id='{E4}'>👑</tg-emoji>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"WELCOME TO REX PRIVATE BOT ZONE! <tg-emoji emoji-id='{E5}'>🌟</tg-emoji>\n"
            f"CURRENT RATE: 1 USD = {DOLAR_RATE} BDT <tg-emoji emoji-id='{E38}'>💱</tg-emoji>\n\n"
            f"PLEASE SELECT AN OPTION: <tg-emoji emoji-id='{E7}'>👇</tg-emoji>"
        )
        await bot.send_message(user_id, welcome_text, parse_mode="HTML", reply_markup=main_menu())
        return

    if data == "binance_sell_option":
        await call.answer()
        
        try:
            await call.message.delete()
        except Exception as e:
            print(e)
            
        user_state[user_id] = {"step": "waiting_amount"}
        
        builder = types.InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="BACK", callback_data="back_to_main_menu"))

        amount_msg = (
            f"ENTER AMOUNT (USD) <tg-emoji emoji-id='{E11}'>💵</tg-emoji>\n\n"
            f"CURRENT RATE: 1 USD = {DOLAR_RATE} BDT <tg-emoji emoji-id='{E38}'>📈</tg-emoji>\n\n"
            f"PLEASE ENTER THE TOTAL DOLLARS YOU WISH TO SELL: <tg-emoji emoji-id='{E7}'>👇</tg-emoji>"
        )
        sent_msg = await bot.send_message(user_id, amount_msg, parse_mode="HTML", reply_markup=builder.as_markup())
        user_state[user_id]["amount_msg_id"] = sent_msg.message_id
        return

    if data == "atm_bkash":
        await call.answer()
        try:
            prev_msg_id = user_state.get(user_id, {}).get("bkash_prompt_msg_id")
            if prev_msg_id:
                await bot.delete_message(call.message.chat.id, prev_msg_id)
        except Exception:
            pass
            
        builder = types.InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="BACK", callback_data="back_to_main_menu"))
        await bot.send_message(user_id, f"PLEASE ENTER YOUR BKASH NUMBER: <tg-emoji emoji-id='{E21}'>📱</tg-emoji>", parse_mode="HTML", reply_markup=builder.as_markup())
        return

    if data in ["dummy_tx", "dummy_sc"]:
        await call.answer()
        return

    if user_id != ADMIN_ID:
        await call.answer("PERMISSION DENIED!", show_alert=True)
        return

    if data.startswith("app_"):
        target_user = int(data.split("_")[1])
        await call.answer("Order approved!")
        
        success_msg = (
            f"━━━━━━━━━━━━━\n"
            f"PAYMENT SUCCESSFUL <tg-emoji emoji-id='{E25}'>✅</tg-emoji>\n"
            f"━━━━━━━━━━━━━\n"
            f"REQUESTED FUNDS HAVE BEEN SUCCESSFULLY SENT TO YOUR PROVIDED NUMBER. <tg-emoji emoji-id='{E26}'>💸</tg-emoji>\n"
            f"━━━━━━━━━━━━━"
        )
        await bot.send_message(target_user, success_msg, parse_mode="HTML", reply_markup=main_menu())
        
        try:
            await call.message.edit_caption(caption=call.message.caption + f"\n\nSTATUS: APPROVED & PAID <tg-emoji emoji-id='{E25}'>✅</tg-emoji>", parse_mode="HTML")
        except Exception:
            await call.message.edit_text(text=call.message.text + f"\n\nSTATUS: APPROVED & PAID <tg-emoji emoji-id='{E25}'>✅</tg-emoji>", parse_mode="HTML")

    elif data.startswith("rej_"):
        target_user = int(data.split("_")[1])
        await call.answer("Order rejected.")
        
        reject_msg = (
            f"━━━━━━━━━━━━━\n"
            f"PAYMENT REJECTED <tg-emoji emoji-id='{E27}'>❌</tg-emoji>\n"
            f"━━━━━━━━━━━━━\n"
            f"YOUR ORDER WAS REJECTED. PLEASE CONTACT SUPPORT. <tg-emoji emoji-id='{E36}'>⚠</tg-emoji>\n"
            f"━━━━━━━━━━━━━"
        )
        await bot.send_message(target_user, reject_msg, parse_mode="HTML", reply_markup=main_menu())
        
        try:
            await call.message.edit_caption(caption=call.message.caption + f"\n\nSTATUS: REJECTED <tg-emoji emoji-id='{E27}'>❌</tg-emoji>", parse_mode="HTML")
        except Exception:
            await call.message.edit_text(text=call.message.text + f"\n\nSTATUS: REJECTED <tg-emoji emoji-id='{E27}'>❌</tg-emoji>", parse_mode="HTML")

    elif data == "admin_toggle":
        bot_status["is_active"] = not bot_status["is_active"]
        status_text = "ACTIVE" if bot_status["is_active"] else "OFF"
        await call.answer(f"BOT STATUS: {status_text}", show_alert=True)

    elif data == "admin_rate":
        await call.answer(f"CURRENT RATE: {DOLAR_RATE} BDT", show_align=True)

    elif data == "admin_broadcast":
        user_state[ADMIN_ID] = {"step": "waiting_broadcast"}
        await bot.send_message(ADMIN_ID, f"PLEASE ENTER YOUR BROADCAST MESSAGE: <tg-emoji emoji-id='{E38}'>📢</tg-emoji>", parse_mode="HTML")

async def main():
    print("Bot is starting on Railway with aiogram 3...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
