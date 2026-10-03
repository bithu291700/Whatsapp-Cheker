import asyncio
import os
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message, CallbackQuery, 
    InlineKeyboardMarkup, InlineKeyboardButton, 
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# ==================== CONFIGURATION ====================
# Apnar bot-er token ekhane bosiye din (athoba environment variable-e set korte paren)
TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

ADMIN_ID = 7388500439          
BINANCE_ID = "123456789"       
ADMIN_USERNAME = "SAIM_X9"     
DOLAR_RATE = 120.0             

bot_status = {"is_active": True}

# ==================== PREMIUM EMOJIS ====================
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

# ==================== KEYBOARDS ====================
def get_main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"{E_MONEY} 𝗦𝗘𝗟𝗟 𝗗𝗢𝗟𝗟𝗘𝗥"), KeyboardButton(text=f"{E_TOOL} 𝗦𝗨𝗣𝗣𝗢𝗥𝗧")],
            [KeyboardButton(text=f"{E_CROWN} 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟")]
        ],
        resize_keyboard=True
    )

def get_binance_inline_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="𝗕𝗜𝗡𝗔𝗡𝗖𝗘", callback_data="binance_sell_option")],
        [InlineKeyboardButton(text="⬅️ 𝗕𝗔𝗖𝗞", callback_data="back_to_main_menu")]
    ])

def get_back_inline_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️️ 𝗕𝗔𝗖𝗞", callback_data="back_to_main_menu")]
    ])

# ==================== FSM STATES ====================
class SellStates(StatesGroup):
    waiting_amount = State()
    waiting_order_id = State()
    waiting_screenshot = State()
    waiting_bkash = State()
    waiting_broadcast = State()

# ==================== HANDLERS ====================
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    if not bot_status["is_active"] and message.from_user.id != ADMIN_ID:
        await message.answer(f"{E_WARNING} 𝗗𝗨𝗞𝗞𝗛𝗜𝗧𝗢! 𝗕𝗢𝗥𝗧𝗢𝗠𝗔𝗡𝗘 𝗔𝗠𝗔𝗗𝗘𝗥 𝗦𝗘𝗥𝗩𝗜𝗖𝗘 𝗕𝗢𝗡𝗗𝗛𝗢 𝗥𝗢𝗬𝗘𝗖𝗛𝗘.", parse_mode="HTML")
        return
    
    await state.clear()
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
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())

@router.message(F.text.contains("𝗦𝗘𝗟𝗟 𝗗𝗢𝗟𝗟𝗘𝗥"))
async def sell_dollar_handler(message: Message):
    msg = (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_HAND} 𝗔𝗦𝗦𝗔𝗟𝗔𝗠𝗨 𝗔𝗟𝗔𝗜𝗞𝗨𝗠\n"
        f"{E_USER} 𝗜'𝗠 𝗦𝗔𝗜𝗠\n"
        f"{E_CROWN} 𝗔𝗗𝗠𝗜𝗡 𝗢𝗙 𝗥𝗘𝗫 𝗣𝗥𝗜𝗩𝗔𝗧𝗘 𝗕𝗢𝗧\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{E_CHART} 𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗥𝗔𝗧𝗘: {DOLAR_RATE} 𝗕𝗗𝗧 / 𝗨𝗦𝗗\n\n"
        f"{E_POINT} 𝗖𝗟𝗜𝗖𝗞 𝗧𝗛𝗘 𝗕𝗨𝗧𝗧𝗢𝗡 𝗕𝗘𝗟𝗢𝗪:"
    )
    await message.answer("Menu hidden", reply_markup=ReplyKeyboardRemove())
    await message.answer(msg, parse_mode="HTML", reply_markup=get_binance_inline_keyboard())

@router.message(F.text.contains("𝗦𝗨𝗣𝗣𝗢𝗥𝗧"))
async def support_handler(message: Message, state: FSMContext):
    await state.clear()
    support_msg = (
        f"{E_TOOL} 𝗖𝗨𝗦𝗧𝗢𝗠𝗘𝗥 𝗦𝗨𝗣𝗣𝗢𝗥𝗧 & 𝗛𝗘𝗟𝗣 𝗗𝗘𝗦𝗞\n\n"
        f"𝗔𝗗𝗠𝗜𝗡 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘: @{ADMIN_USERNAME}"
    )
    await message.answer(support_msg, parse_mode="HTML", reply_markup=get_main_menu_keyboard())

@router.message(F.text.contains("𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟"))
async def admin_panel_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer(f"{E_CROSS} 𝗣𝗘𝗥𝗠𝗜𝗦𝗦𝗜𝗢𝗡 𝗗𝗘𝗡𝗜𝗘𝗗!\n\n𝗨𝗦𝗘𝗥 𝗜𝗗: {message.from_user.id}", parse_mode="HTML", reply_markup=get_main_menu_keyboard())
        return
    
    admin_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧", callback_data="admin_broadcast"),
         InlineKeyboardButton(text="🔄 𝗕𝗢𝗧 𝗢𝗡/𝗢𝗙𝗙", callback_data="admin_toggle")]
    ])
    await message.answer(f"{E_CROWN} 𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗡𝗧𝗥𝗢𝗟 𝗣𝗔𝗡𝗘𝗟", parse_mode="HTML", reply_markup=admin_markup)

@router.callback_query(F.data == "back_to_main_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Returned to Main Menu")
    await state.clear()
    try:
        await callback.message.delete()
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
    await callback.message.answer(welcome_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())

@router.callback_query(F.data == "binance_sell_option")
async def binance_sell_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    await state.set_state(SellStates.waiting_amount)
    
    amount_msg = (
        f"{E_MONEY} 𝗘𝗡𝗧𝗘𝗥 𝗔𝗠𝗢𝗨𝗡𝗧 (𝗨𝗦𝗗)\n\n"
        f"{E_CHART} 𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗥𝗔𝗧𝗘: 1 𝗨𝗦𝗗 = {DOLAR_RATE} 𝗕𝗗𝗧\n\n"
        f"{E_POINT} 𝗣𝗟𝗘𝗔𝗦𝗘 𝗘𝗡𝗧𝗘𝗥 𝗧𝗛𝗘 𝗧𝗢𝗧𝗔𝗟 𝗗𝗢𝗟𝗟𝗔𝗥𝗦 𝗬𝗢𝗨 𝗪𝗜𝗦𝗛 𝗧𝗢 𝗦𝗘𝗟𝗟:"
    )
    sent_msg = await callback.message.answer(amount_msg, parse_mode="HTML", reply_markup=get_back_inline_keyboard())
    await state.update_data(amount_msg_id=sent_msg.message_id)

@router.message(SellStates.waiting_amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        total_taka = amount * DOLAR_RATE
        await state.update_data(amount=amount, total_taka=total_taka)
        await state.set_state(SellStates.waiting_order_id)

        data = await state.get_data()
        try:
            await message.bot.delete_message(message.chat.id, data.get("amount_msg_id"))
        except Exception:
            pass
        try:
            await message.delete()
        except Exception:
            pass

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
        sent_msg = await message.answer(binance_msg, parse_mode="Markdown", reply_markup=get_back_inline_keyboard())
        await state.update_data(binance_msg_id=sent_msg.message_id)
    except ValueError:
        await message.answer(f"{E_WARNING} 𝗣𝗟𝗘𝗔𝗦𝗘 𝗘𝗡𝗧𝗘𝗥 𝗔 𝗩𝗔𝗟𝗜𝗗 𝗡𝗨𝗠𝗕𝗘𝗥!", parse_mode="HTML")

@router.message(SellStates.waiting_order_id)
async def process_order_id(message: Message, state: FSMContext):
    await state.update_data(order_id=message.text)
    await state.set_state(SellStates.waiting_screenshot)
    
    data = await state.get_data()
    try:
        await message.bot.delete_message(message.chat.id, data.get("binance_msg_id"))
    except Exception:
        pass
    try:
        await message.delete()
    except Exception:
        pass

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ 𝗧𝗥𝗔𝗡𝗦𝗔𝗖𝗧𝗜𝗢𝗡 𝗜𝗗", callback_data="dummy_tx"),
         InlineKeyboardButton(text="📸 𝗡𝗘𝗫𝗧 𝗦𝗖𝗥𝗘𝗘𝗡𝗦𝗛𝗢𝗧", callback_data="dummy_sc")],
        [InlineKeyboardButton(text="⬅️️ 𝗕𝗔𝗖𝗞", callback_data="back_to_main_menu")]
    ])

    sent_msg = await message.answer(
        f"━━━━━━━━━━━━━\n"
        f"{E_CHECK} 𝗧𝗥𝗔𝗡𝗦𝗔𝗖𝗧𝗜𝗢𝗡 𝗜𝗗 𝗥𝗘𝗖𝗘𝗜𝗩𝗘𝗗!\n"
        f"━━━━━━━━━━━━━\n\n"
        f"{E_CAMERA} 𝗡𝗢𝗪 𝗣𝗟𝗘𝗔𝗦𝗘 𝗨𝗣𝗟𝗢𝗔𝗗 𝗧𝗛𝗘 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗦𝗖𝗥𝗘𝗘𝗡𝗦𝗛𝗢𝗧 {E_POINT}", 
        parse_mode="HTML",
        reply_markup=markup
    )
    await state.update_data(tx_received_msg_id=sent_msg.message_id)

@router.message(SellStates.waiting_screenshot, F.photo)
async def process_screenshot(message: Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    await state.update_data(photo_file_id=photo_file_id)
    await state.set_state(SellStates.waiting_bkash)
    
    data = await state.get_data()
    try:
        await message.bot.delete_message(message.chat.id, data.get("tx_received_msg_id"))
    except Exception:
        pass
        
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 𝗔𝗧𝗠 𝗕𝗞𝗔𝗦𝗛", callback_data="atm_bkash")],
        [InlineKeyboardButton(text="⬅️ 𝗕𝗔𝗖𝗞", callback_data="back_to_main_menu")]
    ])

    sent_msg = await message.answer(
        f"━━━━━━━━━━━━━\n"
        f"{E_CHECK} 𝗦𝗖𝗥𝗘𝗘𝗡𝗦𝗛𝗢𝗧 𝗥𝗘𝗖𝗘𝗜𝗩𝗘𝗗!\n"
        f"━━━━━━━━━━━━━\n"
        f"{E_BANK} 𝗥𝗘𝗖𝗘𝗜𝗩𝗘 𝗠𝗢𝗡𝗘𝗬 𝗩𝗜𝗔\n"
        f"━━━━━━━━━━━━━\n"
        f"{E_POINT} 𝗦𝗘𝗟𝗘𝗖𝗧 𝗪𝗛𝗘𝗥𝗘 𝗬𝗢𝗨 𝗪𝗔𝗡𝗧 𝗧𝗢 𝗥𝗘𝗖𝗘𝗜𝗩𝗘 𝗬𝗢𝗨𝗥 𝗙𝗨𝗡𝗗𝗦:", 
        parse_mode="HTML",
        reply_markup=markup
    )
    await state.update_data(bkash_prompt_msg_id=sent_msg.message_id)

@router.callback_query(F.data == "atm_bkash")
async def atm_bkash_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    try:
        await callback.message.bot.delete_message(callback.message.chat.id, data.get("bkash_prompt_msg_id"))
    except Exception:
        pass
        
    await callback.message.answer(f"{E_PHONE} 𝗣𝗟𝗘𝗔𝗦𝗘 𝗘𝗡𝗧𝗘𝗥 𝗬𝗢𝗨𝗥 𝗕𝗞𝗔𝗦𝗛 𝗡𝗨𝗠𝗕𝗘𝗥:", parse_mode="HTML", reply_markup=get_back_inline_keyboard())

@router.message(SellStates.waiting_bkash)
async def process_bkash_number(message: Message, state: FSMContext):
    await state.update_data(bkash_number=message.text)
    data = await state.get_data()
    user_id = message.from_user.id
    await state.clear()

    try:
        await message.delete()
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
    await message.answer(summary_msg, parse_mode="HTML", reply_markup=get_main_menu_keyboard())

    admin_notification = (
        f"{E_ALERT} 𝗡𝗘𝗪 𝗗𝗢𝗟𝗟𝗔𝗥 𝗦𝗘𝗟𝗟 𝗢𝗥𝗗𝗘𝗥! {E_ALERT}\n\n"
        f"{E_USER} 𝗨𝗦𝗘𝗥 𝗜𝗗: {user_id}\n"
        f"{E_MONEY} 𝗗𝗢𝗟𝗟𝗔𝗥: {data.get('amount')} 𝗨𝗦𝗗\n"
        f"{E_EXCHANGE} 𝗧𝗔𝗞𝗔: {data.get('total_taka')} 𝗕𝗗𝗧\n"
        f"🆔 𝗢𝗥𝗗𝗘𝗥 𝗜𝗗: {data.get('order_id')}\n"
        f"{E_PHONE} 𝗕𝗞𝗔𝗦𝗛: {data.get('bkash_number')}"
    )
    admin_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘", callback_data=f"app_{user_id}"),
         InlineKeyboardButton(text="❌ 𝗥𝗘𝗝𝗘𝗖𝗧", callback_data=f"rej_{user_id}")]
    ])
    
    if data.get("photo_file_id"):
        await message.bot.send_photo(ADMIN_ID, data.get("photo_file_id"), caption=admin_notification, parse_mode="HTML", reply_markup=admin_markup)
    else:
        await message.bot.send_message(ADMIN_ID, admin_notification, parse_mode="HTML", reply_markup=admin_markup)

@router.callback_query(F.data.startswith("app_") | F.data.startswith("rej_"))
async def admin_decision(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ 𝗣𝗘𝗥𝗠𝗜𝗦𝗦𝗜𝗢𝗡 𝗗𝗘𝗡𝗜𝗘𝗗!", show_alert=True)
        return

    action, target_user_str = callback.data.split("_")
    target_user = int(target_user_str)

    if action == "app":
        await callback.answer("Order approved!")
        success_msg = (
            f"━━━━━━━━━━━━━\n"
            f"{E_CHECK} 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟\n"
            f"━━━━━━━━━━━━━\n"
            f"💸 𝗥𝗘𝗤𝗨𝗘𝗦𝗧𝗘𝗗 𝗙𝗨𝗡𝗗𝗦 𝗛𝗔𝗩𝗘 𝗕𝗘𝗘𝗡 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬 𝗦𝗘𝗡𝗧 𝗧𝗢 𝗬𝗢𝗨𝗥 𝗣𝗥𝗢𝗩𝗜𝗗𝗘𝗗 𝗡𝗨𝗠𝗕𝗘𝗥.\n"
            f"━━━━━━━━━━━━━"
        )
        await callback.bot.send_message(target_user, success_msg, parse_mode="HTML", reply_markup=get_main_menu_keyboard())
        status_text = f"\n\n{E_CHECK} 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 & 𝗣𝗔𝗜𝗗"
    else:
        await callback.answer("Order rejected.")
        reject_msg = (
            f"━━━━━━━━━━━━━\n"
            f"{E_CROSS} 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 𝗥𝗘𝗝𝗘𝗖𝗧𝗘𝗗\n"
            f"━━━━━━━━━━━━━\n"
            f"{E_WARNING} 𝗬𝗢𝗨𝗥 𝗢𝗥𝗗𝗘𝗥 𝗪𝗔𝗦 𝗥𝗘𝗝𝗘𝗖𝗧𝗘𝗗. 𝗣𝗟𝗘𝗔𝗦𝗘 𝗖𝗢𝗡𝗧𝗔𝗖𝗧 𝗦𝗨𝗣𝗣𝗢𝗥𝗧.\n"
            f"━━━━━━━━━━━━━"
        )
        await callback.bot.send_message(target_user, reject_msg, parse_mode="HTML", reply_markup=get_main_menu_keyboard())
        status_text = f"\n\n{E_CROSS} 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗥𝗘𝗝𝗘𝗖𝗧𝗘𝗗"

    try:
        if callback.message.caption:
            await callback.message.edit_caption(caption=callback.message.caption + status_text, parse_mode="HTML", reply_markup=None)
        else:
            await callback.message.edit_text(text=callback.message.text + status_text, parse_mode="HTML", reply_markup=None)
    except Exception:
        pass

@router.callback_query(F.data == "admin_toggle")
async def admin_toggle(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    bot_status["is_active"] = not bot_status["is_active"]
    status_text = "𝗔𝗖𝗧𝗜𝗩𝗘" if bot_status["is_active"] else "𝗢𝗙𝗙"
    await callback.answer(f"𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗨𝗦: {status_text}", show_alert=True)

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_prompt(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.set_state(SellStates.waiting_broadcast)
    await callback.message.answer(f"📢 𝗣𝗟𝗘𝗔𝗦𝗘 𝗘𝗡𝗧𝗘𝗥 𝗬𝗢𝗨𝗥 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗠𝗘𝗦𝗦𝗔𝗚𝗘:", parse_mode="HTML")
    await callback.answer()

@router.message(SellStates.waiting_broadcast, F.from_user.id == ADMIN_ID)
async def execute_broadcast(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f"{E_CHECK} 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗦𝗘𝗡𝗧 (Simulation)", parse_mode="HTML", reply_markup=get_main_menu_keyboard())

# ==================== MAIN FUNCTION ====================
async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    dp.include_router(router)
    
    print("Bot is starting with Aiogram 3.25.0...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
