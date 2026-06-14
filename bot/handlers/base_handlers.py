import json
import os
from aiogram import Router, types, F
from aiogram.filters import CommandStart

router = Router()

def load_keyboards():
    filepath = os.path.join(os.path.dirname(__file__), "..", "ui", "keyboards.json")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from bot.config import OWNER_PIN, STAFF_PIN
from bot.database import supabase_client
from aiogram.utils.keyboard import InlineKeyboardBuilder

class LoginStates(StatesGroup):
    waiting_for_pin = State()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="👨‍💼 ចូលជាម្ចាស់ហាង", callback_data="login_owner"),
        types.InlineKeyboardButton(text="👩‍🔧 ចូលជាបុគ្គលិក", callback_data="login_staff")
    )
    await message.answer("សូមស្វាគមន៍មកកាន់ប្រព័ន្ធគ្រប់គ្រងស្តុក!\n\nតើលោកអ្នកចង់ចូលប្រព័ន្ធក្នុងនាមជាអ្វី?", reply_markup=builder.as_markup())

@router.callback_query(F.data.in_(["login_owner", "login_staff"]))
async def cb_login_selection(callback: types.CallbackQuery, state: FSMContext):
    role = "owner" if callback.data == "login_owner" else "staff"
    await state.update_data(login_role=role)
    await callback.message.answer(f"សូមវាយបញ្ចូលលេខកូដសម្ងាត់ ៤ ខ្ទង់ សម្រាប់ {'ម្ចាស់ហាង' if role == 'owner' else 'បុគ្គលិក'} ៖")
    await state.set_state(LoginStates.waiting_for_pin)
    await callback.answer()

@router.message(LoginStates.waiting_for_pin)
async def process_pin(message: types.Message, state: FSMContext):
    data = await state.get_data()
    role = data.get("login_role")
    pin = message.text.strip()
    
    correct_pin = OWNER_PIN if role == "owner" else STAFF_PIN
    
    if pin != correct_pin:
        await message.answer("❌ លេខកូដមិនត្រឹមត្រូវទេ។ សូមព្យាយាមម្តងទៀត ឬវាយ /start ដើម្បីជ្រើសរើសម្តងទៀត។")
        return
        
    # Update DB
    supabase_client.update_user_role(message.from_user.id, role)
    
    # Show Keyboard
    keyboards = load_keyboards()
    kb_data = keyboards['owner_menu'] if role == 'owner' else keyboards['staff_menu']
    kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(**btn) for btn in row] for row in kb_data['keyboard']],
        resize_keyboard=kb_data.get('resize_keyboard', True)
    )
    
    greeting = "ម្ចាស់ហាង" if role == "owner" else "បុគ្គលិក"
    await message.answer(f"✅ ចូលប្រព័ន្ធជោគជ័យ!\n\nសូមស្វាគមន៍{greeting}! សូមជ្រើសរើសសកម្មភាពខាងក្រោម៖", reply_markup=kb)
    await state.clear()

    # Removed switch_to_staff handler
