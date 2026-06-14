from aiogram import Router, F, types

router = Router()

from bot.database import supabase_client
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

class OwnerStates(StatesGroup):
    waiting_for_batch_update = State()
    waiting_for_branch_name = State()
    waiting_for_new_item = State()
    waiting_for_report_date = State()
    waiting_for_report_month = State()

@router.message(F.text == "📊 របាយការណ៍ប្រចាំថ្ងៃ")
async def cb_daily_report(message: types.Message, state: FSMContext):
    await state.set_state(OwnerStates.waiting_for_report_date)
    await message.answer(
        "សូមជ្រើសរើសកាលបរិច្ឆេទសម្រាប់របាយការណ៍ប្រចាំថ្ងៃ៖",
        reply_markup=await SimpleCalendar().start_calendar()
    )

@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: types.CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        current_state = await state.get_state()
        
        if current_state == OwnerStates.waiting_for_report_date.state:
            date_str = date.strftime("%d/%m/%Y")
            await callback_query.message.edit_text(f"កំពុងទាញយករបាយការណ៍សម្រាប់ថ្ងៃទី {date_str}...")
            await generate_and_send_report(callback_query.message, date_str)
            await state.clear()
            
        elif current_state == OwnerStates.waiting_for_report_month.state:
            month_str = date.strftime("%m/%Y")
            await callback_query.message.edit_text(f"កំពុងទាញយករបាយការណ៍សម្រាប់ខែ {month_str}...")
            await generate_and_send_monthly_report(callback_query.message, month_str)
            await state.clear()

@router.message(OwnerStates.waiting_for_report_date)
async def process_report_custom_date(message: types.Message, state: FSMContext):
    date_str = message.text.strip()
    await message.answer(f"កំពុងទាញយករបាយការណ៍សម្រាប់ថ្ងៃទី {date_str}...")
    success = await generate_and_send_report(message, date_str)
    if success:
        await state.clear()
    # If not success, keep the state to try again

async def generate_and_send_report(message: types.Message, date_str: str):
    transactions = supabase_client.get_daily_transactions(date_str)
    
    if transactions is None:
        await message.answer("ទម្រង់ថ្ងៃខែមិនត្រឹមត្រូវទេ។ សូមវាយបញ្ចូលជាទម្រង់ DD/MM/YYYY (ឧ. 14/06/2026)៖")
        return False
        
    display_date = date_str if date_str else datetime.now().strftime("%d/%m/%Y")
    
    if not transactions:
        await message.answer(f"មិនមានប្រតិបត្តិការណាមួយនៅថ្ងៃទី {display_date} ទេ។")
        return True

    total_sales = 0
    total_items_sold = 0
    total_damage = 0
    
    # Store aggregated sales per item: { 'item_name': {'qty': x, 'price': y, 'total': z} }
    sold_items = {}

    for txn in transactions:
        if txn['type'] == 'sell':
            price = txn.get('items', {}).get('price', 0) if txn.get('items') else 0
            name = txn.get('items', {}).get('name', 'N/A') if txn.get('items') else 'N/A'
            qty = txn['quantity']
            
            total_sales += qty * price
            total_items_sold += qty
            
            if name in sold_items:
                sold_items[name]['qty'] += qty
                sold_items[name]['total'] += qty * price
            else:
                sold_items[name] = {'qty': qty, 'price': price, 'total': qty * price}
                
        elif txn['type'] == 'damage':
            total_damage += txn['quantity']
            
    report_text = f"📊 **របាយការណ៍លក់ប្រចាំថ្ងៃ: {display_date}**\n"
    report_text += "-----------------------\n"
    
    if sold_items:
        i = 1
        for name, data in sold_items.items():
            report_text += f"{i}. {name} ({data['qty']} ✕ ${data['price']:.2f}) = ${data['total']:.2f}\n"
            i += 1
    else:
        report_text += "គ្មានការលក់ចេញទេ\n"
        
    report_text += "-----------------------\n"
    report_text += f"🛒 ចំនួនទំនិញលក់ចេញសរុប: {total_items_sold}\n"
    report_text += f"💵 ចំណូលសរុប: ${total_sales:.2f}\n"
    report_text += f"⚠️ ចំនួនទំនិញខូចខាត: {total_damage}\n"
    
    await message.answer(report_text, parse_mode="Markdown")
    return True

@router.message(F.text == "📊 របាយការណ៍ប្រចាំខែ")
async def cb_monthly_report(message: types.Message, state: FSMContext):
    await state.set_state(OwnerStates.waiting_for_report_month)
    await message.answer(
        "សូមជ្រើសរើសថ្ងៃណាមួយក្នុងខែដែលអ្នកចង់មើលរបាយការណ៍ប្រចាំខែ៖",
        reply_markup=await SimpleCalendar().start_calendar()
    )


@router.message(OwnerStates.waiting_for_report_month)
async def process_report_custom_month(message: types.Message, state: FSMContext):
    month_str = message.text.strip()
    await message.answer(f"កំពុងទាញយករបាយការណ៍សម្រាប់ខែ {month_str}...")
    success = await generate_and_send_monthly_report(message, month_str)
    if success:
        await state.clear()

async def generate_and_send_monthly_report(message: types.Message, month_str: str):
    transactions = supabase_client.get_monthly_transactions(month_str)
    
    if transactions is None:
        await message.answer("ទម្រង់ខែឆ្នាំមិនត្រឹមត្រូវទេ។ សូមវាយបញ្ចូលជាទម្រង់ MM/YYYY (ឧ. 06/2026)៖")
        return False
        
    display_month = month_str if month_str else datetime.now().strftime("%m/%Y")
    
    if not transactions:
        await message.answer(f"មិនមានប្រតិបត្តិការណាមួយនៅខែ {display_month} ទេ។")
        return True

    total_sales = 0
    total_items_sold = 0
    total_damage = 0
    
    sold_items = {}

    for txn in transactions:
        if txn['type'] == 'sell':
            price = txn.get('items', {}).get('price', 0) if txn.get('items') else 0
            name = txn.get('items', {}).get('name', 'N/A') if txn.get('items') else 'N/A'
            qty = txn['quantity']
            
            total_sales += qty * price
            total_items_sold += qty
            
            if name in sold_items:
                sold_items[name]['qty'] += qty
                sold_items[name]['total'] += qty * price
            else:
                sold_items[name] = {'qty': qty, 'price': price, 'total': qty * price}
                
        elif txn['type'] == 'damage':
            total_damage += txn['quantity']
            
    report_text = f"📊 **របាយការណ៍លក់ប្រចាំខែ: {display_month}**\n"
    report_text += "-----------------------\n"
    
    if sold_items:
        i = 1
        for name, data in sold_items.items():
            report_text += f"{i}. {name} ({data['qty']} ✕ ${data['price']:.2f}) = ${data['total']:.2f}\n"
            i += 1
    else:
        report_text += "គ្មានការលក់ចេញទេ\n"
        
    report_text += "-----------------------\n"
    report_text += f"🛒 ចំនួនទំនិញលក់ចេញសរុប: {total_items_sold}\n"
    report_text += f"💵 ចំណូលសរុប: ${total_sales:.2f}\n"
    report_text += f"⚠️ ចំនួនទំនិញខូចខាត: {total_damage}\n"
    
    await message.answer(report_text, parse_mode="Markdown")
    return True


import os
import uuid
import pandas as pd
from aiogram.types import FSInputFile

@router.message(F.text == "📥 ទាញយកជា Excel")
async def cb_export_excel(message: types.Message):
    await message.answer("កំពុងរៀបចំឯកសារ Excel...")
    
    inventory = supabase_client.get_all_inventory()
    if not inventory:
        await message.answer("មិនមានទិន្នន័យស្តុកទំនិញទេ។")
        return
        
    data = []
    for item in inventory:
        data.append({
            "លេខបាកូដ (Barcode)": item.get('items', {}).get('barcode', ''),
            "ឈ្មោះទំនិញ (Name)": item.get('items', {}).get('name', ''),
            "តម្លៃ (Price)": item.get('items', {}).get('price', 0),
            "សាខា (Branch)": item.get('branches', {}).get('name', 'N/A') if item.get('branches') else 'N/A',
            "ចំនួនស្តុក (Quantity)": item.get('quantity', 0),
            "ធ្វើបច្ចុប្បន្នភាពចុងក្រោយ (Updated At)": item.get('updated_at', '')
        })
        
    df = pd.DataFrame(data)
    filename = f"inventory_report_{uuid.uuid4().hex[:8]}.xlsx"
    filepath = os.path.join(os.getenv("TEMP", "."), filename)
    
    df.to_excel(filepath, index=False)
    
    doc = FSInputFile(filepath)
    await message.answer_document(doc, caption="📊 របាយការណ៍ស្តុកទំនិញ")
    
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception:
        pass


@router.message(F.text == "⚙️ កែប្រែស្តុកច្រើនដង")
async def cb_batch_update(message: types.Message, state: FSMContext):
    await message.answer("សូមបញ្ជូនទិន្នន័យកែប្រែក្នុងទម្រង់ខាងក្រោម៖\nលេខបាកូដ: +ចំនួន\nឧទាហរណ៍៖\n12345: +50")
    await state.set_state(OwnerStates.waiting_for_batch_update)

@router.message(OwnerStates.waiting_for_batch_update)
async def process_batch_update(message: types.Message, state: FSMContext, user_role: str, branch_id: str):
    if not branch_id:
        await message.answer("អ្នកមិនទាន់មានសាខាប្រចាំការទេ។ សូមចូលទៅកាន់ ការកំណត់សាខា ជាមុនសិន។")
        await state.clear()
        return

    lines = message.text.strip().split('\n')
    success_count = 0
    errors = []
    
    for line in lines:
        if ':' not in line:
            continue
        parts = line.split(':')
        barcode = parts[0].strip()
        try:
            qty_str = parts[1].strip()
            qty = int(qty_str.replace('+', ''))
        except ValueError:
            errors.append(f"ចំនួនមិនត្រឹមត្រូវសម្រាប់បាកូដ {barcode}")
            continue
            
        item = supabase_client.get_item_by_barcode(barcode)
        if not item:
            errors.append(f"រកមិនឃើញទំនិញបាកូដ: {barcode}")
            continue
            
        supabase_client.upsert_inventory(item['id'], branch_id, qty)
        supabase_client.log_transaction(item['id'], branch_id, message.from_user.id, 'batch_update', qty)
        success_count += 1
        
    reply = f"✅ បានកែប្រែស្តុកជោគជ័យចំនួន {success_count} មុខ។"
    if errors:
        reply += "\n⚠️ បញ្ហាដែលបានជួបប្រទះ៖\n" + "\n".join(errors)
        
    await message.answer(reply)
    await state.clear()

@router.message(F.text == "📋 មើលបញ្ជីទំនិញទាំងអស់")
async def cb_view_all_items(message: types.Message, branch_id: str):
    inventory = supabase_client.get_all_inventory()
    
    if not inventory:
        await message.answer("មិនទាន់មានទំនិញក្នុងស្តុកទេ។")
        return
        
    # Filter by branch if owner is assigned to a branch, else show all
    if branch_id:
        inventory = [inv for inv in inventory if inv['branch_id'] == branch_id]
        
    if not inventory:
        await message.answer("មិនទាន់មានទំនិញក្នុងសាខារបស់អ្នកទេ។")
        return

    text = "📋 **បញ្ជីទំនិញទាំងអស់ក្នុងស្តុក៖**\n\n"
    for i, inv in enumerate(inventory, 1):
        item = inv.get('items', {})
        name = item.get('name', 'N/A')
        barcode = item.get('barcode', 'N/A')
        price = item.get('price', 0)
        qty = inv.get('quantity', 0)
        
        text += f"**{i}. 📦 {name}** (`{barcode}`)\n"
        text += f"   • ស្តុកសល់: {qty} | តម្លៃ: ${price:.2f}\n\n"
        
        # Telegram max length is 4096, split if too long
        if len(text) > 3800:
            await message.answer(text, parse_mode="Markdown")
            text = ""
            
    if text.strip():
        await message.answer(text, parse_mode="Markdown")

@router.message(F.text == "📜 ប្រវត្តិស្តុក")
async def cb_stock_history(message: types.Message):
    # Get today's transactions
    transactions = supabase_client.get_daily_transactions()
    
    if not transactions:
        await message.answer("មិនមានប្រតិបត្តិការស្តុកនៅថ្ងៃនេះទេ។")
        return
        
    grouped_txns = {
        'restock': [],
        'sell': [],
        'batch_update': [],
        'damage': [],
        'undo': []
    }
    
    for txn in transactions:
        txn_type = txn.get('type')
        if txn_type in grouped_txns:
            grouped_txns[txn_type].append(txn)
            
    text = "📜 **ប្រវត្តិប្រតិបត្តិការស្តុកថ្ងៃនេះ**\n\n"
    
    sections = [
        ('restock', '🟢 **បញ្ចូលស្តុក (Restock)**', '+'),
        ('sell', '🔴 **លក់ចេញ (Sell)**', '-'),
        ('batch_update', '⚙️ **កែតម្រូវ (Batch Update)**', ''),
        ('damage', '⚠️ **ខូចខាត (Damage)**', '-'),
        ('undo', '↩️ **ត្រលប់ប្រតិបត្តិការ (Undo)**', '+'),
    ]
    
    for key, title, sign in sections:
        if grouped_txns[key]:
            text += f"{title}\n"
            for txn in grouped_txns[key]:
                item_name = txn.get('items', {}).get('name', 'N/A') if txn.get('items') else 'N/A'
                qty = txn['quantity']
                
                # Parse time
                try:
                    created_at = datetime.fromisoformat(txn['created_at'].replace('Z', '+00:00'))
                    local_time = created_at + timedelta(hours=7)
                    time_str = local_time.strftime("%I:%M %p")
                except:
                    time_str = "N/A"
                    
                text += f"• `{time_str}` | {item_name} ({sign}{qty})\n"
                
                # Telegram max length is 4096, split if too long
                if len(text) > 3800:
                    await message.answer(text, parse_mode="Markdown")
                    text = ""
            text += "\n"
            
    if text.strip():
        await message.answer(text, parse_mode="Markdown")

@router.message(F.text == "🏢 ការកំណត់សាខា")
async def cb_branch_settings(message: types.Message):
    branches = supabase_client.get_all_branches()
    
    builder = InlineKeyboardBuilder()
    for b in branches:
        builder.row(types.InlineKeyboardButton(text=f"🏢 {b['name']}", callback_data=f"select_branch_{b['id']}"))
        
    builder.row(types.InlineKeyboardButton(text="➕ បន្ថែមសាខាថ្មី", callback_data="add_new_branch"))
    
    await message.answer("សូមជ្រើសរើសសាខា ឬបន្ថែមសាខាថ្មី៖", reply_markup=builder.as_markup())

@router.message(F.text == "➕ បន្ថែមទំនិញថ្មី")
async def process_add_new_item_btn(message: types.Message, state: FSMContext):
    msg = (
        "សូមបញ្ជូនទិន្នន័យទំនិញថ្មីក្នុងទម្រង់ខាងក្រោម (អាចបញ្ជូន១ជួរ ឬច្រើនជួរផ្ទួនគ្នាបាន)៖\n\n"
        "`បាកូដ | ឈ្មោះទំនិញ | តម្លៃ | ស្តុកដំបូង`\n\n"
        "**ឧទាហរណ៍បញ្ចូលម្តង១៖**\n"
        "`8851234567 | ទឹកអូអ៊ីឈិ | 0.5 | 100`\n\n"
        "**ឧទាហរណ៍បញ្ចូលម្តងច្រើនមុខ៖**\n"
        "`គ្មាន | មីម៉ាម៉ា | 0.25 | 200`\n"
        "`គ្មាន | ត្រីខកំប៉ុង | 0.8 | 50`\n"
        "`123456 | ទឹកសុទ្ធ | 0.25 | 300`\n\n"
        "*(បញ្ជាក់៖ សូមប្រើសញ្ញាបញ្ឈរ | ដើម្បីខណ្ឌចែក)*"
    )
    await message.answer(msg, parse_mode="Markdown")
    await state.set_state(OwnerStates.waiting_for_new_item)

@router.message(OwnerStates.waiting_for_new_item)
async def handle_new_item_data(message: types.Message, state: FSMContext, branch_id: str):
    if not branch_id:
        await message.answer("អ្នកមិនទាន់មានសាខាប្រចាំការទេ។ សូមចូលទៅកាន់ ការកំណត់សាខា ជាមុនសិន។")
        await state.clear()
        return
        
    lines = message.text.strip().split('\n')
    success_count = 0
    errors = []
    
    for line in lines:
        if not line.strip():
            continue
            
        parts = line.split('|')
        if len(parts) != 4:
            errors.append(f"ទម្រង់ខុស៖ {line}")
            continue
            
        barcode = parts[0].strip()
        name = parts[1].strip()
        
        try:
            price = float(parts[2].strip())
            stock = int(parts[3].strip())
        except ValueError:
            errors.append(f"តម្លៃ/ស្តុកខុស៖ {line}")
            continue
            
        item, err = supabase_client.add_new_item(barcode, name, price, branch_id, stock)
        
        if item:
            supabase_client.log_transaction(item['id'], branch_id, message.from_user.id, 'restock', stock)
            success_count += 1
        else:
            errors.append(f"បរាជ័យ ({err}): {name}")
            
    # Send summary message
    reply_text = f"✅ បានបន្ថែមទំនិញថ្មីដោយជោគជ័យចំនួន {success_count} មុខ។"
    if errors:
        reply_text += "\n\n⚠️ បញ្ហាដែលបានជួបប្រទះ៖\n" + "\n".join(errors)
        
    reply_text += "\n\nតើលោកអ្នកចង់បន្ថែមទំនិញថ្មីបន្តទៀតដែរឬទេ?"
    
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="➕ បន្តបន្ថែមទៀត", callback_data="add_more_item"),
        types.InlineKeyboardButton(text="❌ បញ្ឈប់", callback_data="stop_add_item")
    )
    
    await message.answer(reply_text, reply_markup=builder.as_markup())
    await state.clear()

@router.callback_query(F.data == "add_more_item")
async def cb_add_more_item(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(callback.message.text + "\n\n*(បន្តការបញ្ចូល)*")
    msg = "សូមបញ្ជូនទិន្នន័យទំនិញបន្ទាប់ (អាចវាយ១មុខ ឬច្រើនមុខបាន)៖\n`បាកូដ | ឈ្មោះទំនិញ | តម្លៃ | ស្តុកដំបូង`"
    await callback.message.answer(msg, parse_mode="Markdown")
    await state.set_state(OwnerStates.waiting_for_new_item)
    await callback.answer()

@router.callback_query(F.data == "stop_add_item")
async def cb_stop_add_item(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(callback.message.text + "\n\n*(បានបញ្ឈប់)*")
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "add_new_branch")
async def cb_add_branch(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("សូមវាយបញ្ចូលឈ្មោះសាខាថ្មី៖")
    await state.set_state(OwnerStates.waiting_for_branch_name)
    await callback.answer()

@router.message(OwnerStates.waiting_for_branch_name)
async def process_add_branch(message: types.Message, state: FSMContext):
    name = message.text.strip()
    branch = supabase_client.add_branch(name)
    if branch:
        await message.answer(f"✅ បានបន្ថែមសាខាថ្មី៖ {name}")
    else:
        await message.answer("❌ មានបញ្ហាក្នុងការបន្ថែមសាខា។")
    await state.clear()

@router.callback_query(F.data.startswith("select_branch_"))
async def cb_select_branch(callback: types.CallbackQuery):
    branch_id = callback.data.split("select_branch_")[1]
    supabase_client.set_user_branch(callback.from_user.id, branch_id)
    await callback.message.answer("✅ បានកំណត់សាខាប្រចាំការរបស់អ្នកជោគជ័យ។ ចាប់ពីពេលនេះទៅ រាល់ប្រតិបត្តិការរបស់អ្នកនឹងត្រូវបានកត់ត្រាក្នុងសាខានេះ។")
    await callback.answer()
