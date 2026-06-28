import json
import os
from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command

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

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "ℹ️ <b>ជំនួយ / Help</b>\n\n"
        "🔑 <b>ការណែនាំអំពីការប្រើប្រាស់ (How to use):</b>\n"
        "សូមប្រើប្រាស់ប៊ូតុងនៅលើក្តារចុច (Keyboard buttons) ឬវាយពាក្យបញ្ជាខាងក្រោម៖\n\n"
        "👤 <b>សម្រាប់ម្ចាស់ហាង (Owner):</b>\n"
        "• 📊 របាយការណ៍ប្រចាំថ្ងៃ ៖ មើលរបាយការណ៍លក់ប្រចាំថ្ងៃ\n"
        "• 📊 របាយការណ៍ប្រចាំខែ ៖ មើលរបាយការណ៍លក់ប្រចាំខែ\n"
        "• 📥 ទាញយកជា Excel ៖ ទាញយករបាយការណ៍ស្តុកទំនិញ\n"
        "• ⚙️ កែប្រែស្តុកច្រើនដង ៖ កែប្រែស្តុកទំនិញលឿនរហ័ស\n"
        "• 📋 មើលបញ្ជីទំនិញទាំងអស់ ៖ មើលបញ្ជីរាយនាមទំនិញទាំងអស់\n"
        "• 📜 ប្រវត្តិស្តុក ៖ មើលប្រវត្តិប្រតិបត្តិការស្តុកថ្ងៃនេះ\n"
        "• 🏢 ការកំណត់សាខា ៖ កំណត់ ឬបន្ថែម/លុបសាខាហាង\n"
        "• ➕ បន្ថែមទំនិញថ្មី ៖ បន្ថែមទំនិញថ្មីចូលស្តុក\n"
        "• 🗑 លុបទំនិញ ៖ លុបទំនិញចេញពីប្រព័ន្ធ\n"
        "• 🔍 ស្វែងរក / ពិនិត្យស្តុក ៖ ស្វែងរកទំនិញតាមឈ្មោះ/បាកូដ\n"
        "• 🛒 បង់ប្រាក់រហ័ស ៖ បញ្ចូលការលក់ទំនិញរហ័ស\n"
        "• ⚠️ រាយការណ៍ទំនិញខូច ៖ កត់ត្រាទំនិញខូចខាត\n\n"
        "🔄 <b>ផ្សេងៗ (Other Commands):</b>\n"
        "• /start - ចាប់ផ្តើមឡើងវិញ ឬជ្រើសរើសតួនាទីថ្មី (Restart / Select Role)\n"
        "• /help - បង្ហាញសារជំនួយនេះ (Show help message)"
    )
    await message.answer(help_text)

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
    full_name = message.from_user.full_name
    supabase_client.update_user_role(message.from_user.id, role, full_name)
    
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
