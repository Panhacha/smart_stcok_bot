from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from bot.database import supabase_client
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json
import os
import datetime

router = Router()

def load_keyboards():
    filepath = os.path.join(os.path.dirname(__file__), "..", "ui", "keyboards.json")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

class StaffStates(StatesGroup):
    waiting_for_search_query = State()
    waiting_for_checkout_barcode = State()
    waiting_for_custom_checkout_qty = State()
    waiting_for_damage_barcode = State()
    waiting_for_damage_photo = State()
@router.message(F.text == "🔍 ស្វែងរក / ពិនិត្យស្តុក")
async def process_search_stock(message: types.Message, state: FSMContext, branch_id: str):
    inventory = supabase_client.get_all_inventory()
    
    if not inventory:
        await message.answer("មិនទាន់មានទំនិញក្នុងប្រព័ន្ធទេ។ សូមម្ចាស់ហាងបញ្ចូលទំនិញជាមុនសិន។")
        return
        
    if branch_id:
        inventory = [inv for inv in inventory if inv['branch_id'] == branch_id]
        
    if not inventory:
        await message.answer("មិនទាន់មានទំនិញក្នុងសាខារបស់អ្នកទេ។")
        return
        
    builder = InlineKeyboardBuilder()
    
    # Sort by name
    inventory = sorted(inventory, key=lambda x: x.get('items', {}).get('name', ''))
    
    for inv in inventory[:60]: # Limit to 60 buttons max
        item = inv.get('items', {})
        if not item: continue
        name = item.get('name', 'N/A')
        qty = inv.get('quantity', 0)
        item_id = inv.get('item_id')
        
        # Format: 📦 Name (10)
        btn_text = f"📦 {name} ({qty})"
        builder.add(types.InlineKeyboardButton(text=btn_text, callback_data=f"show_item_{item_id}"))
        
    builder.adjust(2) # 2 columns per row
    await message.answer("សូមជ្រើសរើសទំនិញដែលលោកអ្នកចង់ពិនិត្យមើល៖", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("show_item_"))
async def cb_show_item(callback: types.CallbackQuery, branch_id: str):
    item_id = callback.data.split("show_item_")[1]
    
    response = supabase_client.supabase.table("items").select("*").eq("id", item_id).execute()
    if not response.data:
        await callback.answer("រកមិនឃើញទំនិញនេះទេ!", show_alert=True)
        return
        
    item = response.data[0]
    inv = supabase_client.get_inventory(item['id'], branch_id) if branch_id else None
    qty = inv['quantity'] if inv else 0
    
    text = f"📦 **ទំនិញ:** {item['name']}\n🔢 **បាកូដ:** {item['barcode']}\n💵 **តម្លៃ:** ${item['price']:.2f}\n📊 **ស្តុកសល់:** {qty}"
    
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="➖ កាត់ស្តុកចេញ", callback_data=f"cout_{item['id']}"),
        types.InlineKeyboardButton(text="➕ បន្ថែមស្តុកចូល", callback_data=f"cin_{item['id']}")
    )
    if qty <= 0:
        builder.row(types.InlineKeyboardButton(text="🌐 ពិនិត្យមើលសាខាផ្សេងទៀត", callback_data=f"check_branch_stock_{item['id']}"))
        
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("check_branch_stock_"))
async def check_cross_branch(callback: types.CallbackQuery, branch_id: str):
    item_id = callback.data.split("check_branch_stock_")[1]
    results = supabase_client.check_nearby_branches(item_id, branch_id if branch_id else "")
    
    if not results:
        await callback.message.answer("❌ គ្រប់សាខាទាំងអស់សុទ្ធតែអស់ស្តុកទំនិញនេះ។")
    else:
        text = "🏢 **ស្តុកនៅសាខាផ្សេងទៀត៖**\n\n"
        for r in results:
            text += f"▪️ {r.get('branches', {}).get('name', 'N/A')}: {r['quantity']} ឯកតា\n"
        await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@router.message(F.text == "🛒 បង់ប្រាក់រហ័ស")
async def process_quick_checkout(message: types.Message, state: FSMContext):
    await message.answer("សូមស្កេនបាកូដ ឬវាយបញ្ចូលលេខបាកូដទំនិញដើម្បីបង់ប្រាក់។ (វាយ 'បញ្ឈប់' ដើម្បីចេញ)")
    await state.set_state(StaffStates.waiting_for_checkout_barcode)

async def _do_stock_update(message: types.Message, item: dict, qty: int, branch_id: str, is_add: bool):
    if not branch_id:
        await message.answer("❌ អ្នកមិនទាន់មានសាខាប្រចាំការទេ។")
        return

    inv = supabase_client.get_inventory(item['id'], branch_id)
    current_qty = inv['quantity'] if inv else 0
    
    if not is_add and current_qty < qty:
        await message.answer(f"❌ ទំនិញ {item['name']} មិនមានស្តុកគ្រប់គ្រាន់ទេ! (សល់តែ {current_qty})")
        return

    change = qty if is_add else -qty
    new_qty = current_qty + change
    supabase_client.upsert_inventory(item['id'], branch_id, change)
    
    txn_type = 'restock' if is_add else 'sell'
    txn = supabase_client.log_transaction(item['id'], branch_id, message.from_user.id, txn_type, qty)
    
    builder = InlineKeyboardBuilder()
    if txn:
        builder.row(types.InlineKeyboardButton(text="↩️ លុបចោលវិញ (Undo)", callback_data=f"undo_{txn['id']}"))
        
    action_text = "បន្ថែមស្តុកចូល" if is_add else "លក់"
    await message.answer(f"✅ បាន{action_text} **{item['name']}** ចំនួន {qty}\n📊 ស្តុកឥឡូវមាន: {new_qty}", reply_markup=builder.as_markup(), parse_mode="Markdown")
    
    # Low stock alert
    if not is_add:
        threshold = item.get('low_stock_threshold', 10)
        if new_qty <= threshold:
            owners = supabase_client.get_owners()
            alert_msg = f"⚠️ **Low Stock Alert!**\nទំនិញ: {item['name']}\nស្តុកនៅសល់: {new_qty}"
            for owner_id in owners:
                try:
                    await message.bot.send_message(owner_id, alert_msg, parse_mode="Markdown")
                except Exception:
                    pass

async def execute_checkout(message: types.Message, text_input: str, branch_id: str):
    parts = text_input.strip().split()
    barcode = parts[0]
    qty_to_deduct = 1
    if len(parts) > 1:
        try:
            qty_to_deduct = int(parts[1])
        except ValueError:
            pass

    item = supabase_client.get_item_by_barcode(barcode)
    if not item:
        await message.answer(f"❌ រកមិនឃើញទំនិញបាកូដ: {barcode}")
        return

    await _do_stock_update(message, item, qty_to_deduct, branch_id, is_add=False)

@router.message(StaffStates.waiting_for_checkout_barcode)
async def handle_checkout_barcode(message: types.Message, branch_id: str, state: FSMContext):
    barcode = message.text.strip()
    if barcode.lower() == 'បញ្ឈប់':
        await message.answer("បានបញ្ឈប់ការបង់ប្រាក់។")
        await state.clear()
        return
        
    await execute_checkout(message, barcode, branch_id)

@router.callback_query(F.data.startswith("cout_"))
async def cb_custom_out(callback: types.CallbackQuery, state: FSMContext):
    item_id = callback.data.split("cout_")[1]
    await state.update_data(target_item_id=item_id, is_add=False)
    await callback.message.answer("🔻 សូមវាយបញ្ចូលចំនួនដែលភ្ញៀវបានទិញ (ដកចេញពីស្តុក)៖")
    await state.set_state(StaffStates.waiting_for_custom_checkout_qty)
    await callback.answer()

@router.callback_query(F.data.startswith("cin_"))
async def cb_custom_in(callback: types.CallbackQuery, state: FSMContext):
    item_id = callback.data.split("cin_")[1]
    await state.update_data(target_item_id=item_id, is_add=True)
    await callback.message.answer("🔺 សូមវាយបញ្ចូលចំនួនដែលចង់បញ្ចូលបន្ថែម (បូកចូលស្តុក)៖")
    await state.set_state(StaffStates.waiting_for_custom_checkout_qty)
    await callback.answer()

@router.message(StaffStates.waiting_for_custom_checkout_qty)
async def process_custom_checkout_qty(message: types.Message, state: FSMContext, branch_id: str):
    qty_str = message.text.strip()
    try:
        qty = int(qty_str)
        if qty <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ ចំនួនមិនត្រឹមត្រូវទេ។ សូមវាយជាលេខធំជាង 0។")
        return
        
    data = await state.get_data()
    item_id = data.get("target_item_id")
    is_add = data.get("is_add", False)
    
    response = supabase_client.supabase.table("items").select("*").eq("id", item_id).execute()
    if not response.data:
        await message.answer("❌ រកមិនឃើញទំនិញនេះទេ។")
        await state.clear()
        return
        
    item = response.data[0]
    await _do_stock_update(message, item, qty, branch_id, is_add)
    await state.clear()

@router.callback_query(F.data.startswith("undo_"))
async def cb_undo(callback: types.CallbackQuery, branch_id: str):
    txn_id = callback.data.split("undo_")[1]
    txn = supabase_client.get_transaction(txn_id)
    
    if not txn or txn['status'] == 'reversed':
        await callback.message.answer("❌ ប្រតិបត្តិការនេះត្រូវបានលុបចោលរួចហើយ ឬរកមិនឃើញ។")
        await callback.answer()
        return
        
    created_at = datetime.datetime.fromisoformat(txn['created_at'].replace('Z', '+00:00'))
    now = datetime.datetime.now(datetime.timezone.utc)
    if (now - created_at).total_seconds() > 300: # Allow 5 minutes instead of 30s to be safe
        await callback.message.answer("❌ ហួសពេលកំណត់ក្នុងការលុបចោល។")
        await callback.answer()
        return
        
    # Reverse
    supabase_client.upsert_inventory(txn['item_id'], txn['branch_id'], txn['quantity'])
    supabase_client.update_transaction_status(txn_id, 'reversed')
    supabase_client.log_transaction(txn['item_id'], txn['branch_id'], callback.from_user.id, 'undo', txn['quantity'])
    
    await callback.message.answer("✅ បានលុបចោលប្រតិបត្តិការជោគជ័យ និងបន្ថែមស្តុកត្រឡប់វិញ។")
    await callback.answer()

@router.message(F.text == "⚠️ រាយការណ៍ទំនិញខូច")
async def process_report_damage(message: types.Message, state: FSMContext):
    await message.answer("សូមវាយបញ្ចូលបាកូដ និងចំនួនទំនិញដែលខូចខាត (ឧ. `12345 2`)៖", parse_mode="Markdown")
    await state.set_state(StaffStates.waiting_for_damage_barcode)

@router.message(StaffStates.waiting_for_damage_barcode)
async def handle_damage_barcode(message: types.Message, state: FSMContext):
    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.answer("❌ ទម្រង់មិនត្រឹមត្រូវ។ សូមវាយ `បាកូដ ចំនួន` (ឧ. `12345 2`)")
        return
        
    barcode, qty_str = parts[0], parts[1]
    try:
        qty = int(qty_str)
    except ValueError:
        await message.answer("❌ ចំនួនត្រូវតែជាលេខ។")
        return
        
    item = supabase_client.get_item_by_barcode(barcode)
    if not item:
        await message.answer("❌ រកមិនឃើញទំនិញបាកូដនេះទេ។")
        return
        
    await state.update_data(damage_item_id=item['id'], damage_qty=qty)
    await message.answer("សូមផ្ញើរូបភាពទំនិញដែលខូចខាតមកកាន់ខ្ញុំ៖")
    await state.set_state(StaffStates.waiting_for_damage_photo)

@router.message(StaffStates.waiting_for_damage_photo, F.photo)
async def handle_damage_photo(message: types.Message, state: FSMContext, branch_id: str):
    if not branch_id:
        await message.answer("❌ អ្នកមិនទាន់មានសាខាប្រចាំការទេ។")
        await state.clear()
        return
        
    photo_file_id = message.photo[-1].file_id
    data = await state.get_data()
    item_id = data['damage_item_id']
    qty = data['damage_qty']
    
    supabase_client.upsert_inventory(item_id, branch_id, -qty)
    supabase_client.report_damage(item_id, branch_id, message.from_user.id, qty, photo_file_id)
    supabase_client.log_transaction(item_id, branch_id, message.from_user.id, 'damage', qty)
    
    await message.answer("✅ បានរាយការណ៍ទំនិញខូចខាត និងកាត់ស្តុកដោយជោគជ័យ។")
    await state.clear()

@router.message(F.web_app_data)
async def handle_webapp_data(message: types.Message, branch_id: str):
    barcode = message.web_app_data.data.strip()
    await execute_checkout(message, barcode, branch_id)
