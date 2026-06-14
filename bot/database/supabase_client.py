from supabase import create_client, Client
from bot.config import SUPABASE_URL, SUPABASE_KEY
from datetime import datetime, timezone, timedelta

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_user(telegram_id: int):
    response = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
    return response.data[0] if response.data else None

def get_item_by_barcode(barcode: str):
    response = supabase.table("items").select("*").eq("barcode", barcode).execute()
    return response.data[0] if response.data else None

def add_new_item(barcode: str, name: str, price: float, branch_id: str, initial_stock: int):
    # 1. Check if barcode already exists
    if barcode and barcode != 'គ្មាន':
        existing = get_item_by_barcode(barcode)
        if existing:
            return None, "បាកូដនេះមានរួចហើយក្នុងប្រព័ន្ធ!"
            
    # 2. Insert Item
    item_data = {
        "name": name,
        "price": price
    }
    if barcode and barcode != 'គ្មាន':
        item_data['barcode'] = barcode
        
    try:
        res_item = supabase.table("items").insert(item_data).execute()
        item = res_item.data[0]
        
        # 3. Add initial inventory
        if branch_id:
            upsert_inventory(item['id'], branch_id, initial_stock)
            
        return item, "ជោគជ័យ"
    except Exception as e:
        return None, str(e)

def get_inventory(item_id: str, branch_id: str):
    response = supabase.table("inventory").select("*").eq("item_id", item_id).eq("branch_id", branch_id).execute()
    return response.data[0] if response.data else None

def check_nearby_branches(item_id: str, current_branch_id: str):
    response = supabase.table("inventory").select("*, branches(name, location)").eq("item_id", item_id).neq("branch_id", current_branch_id).gt("quantity", 0).execute()
    return response.data

def log_transaction(item_id: str, branch_id: str, user_id: int, txn_type: str, quantity: int):
    data = {
        "item_id": item_id,
        "branch_id": branch_id,
        "user_id": user_id,
        "type": txn_type,
        "quantity": quantity
    }
    response = supabase.table("transactions").insert(data).execute()
    return response.data[0] if response.data else None

def deduct_inventory(item_id: str, branch_id: str, quantity: int):
    # Fetch current
    current = get_inventory(item_id, branch_id)
    if not current or current['quantity'] < quantity:
        return False
    
    new_quantity = current['quantity'] - quantity
    response = supabase.table("inventory").update({"quantity": new_quantity}).eq("item_id", item_id).eq("branch_id", branch_id).execute()
    return response.data[0] if response.data else None

def report_damage(item_id: str, branch_id: str, user_id: int, quantity: int, photo_file_id: str):
    data = {
        "item_id": item_id,
        "branch_id": branch_id,
        "user_id": user_id,
        "quantity": quantity,
        "photo_file_id": photo_file_id
    }
    response = supabase.table("defect_logs").insert(data).execute()
    return response.data[0] if response.data else None

def get_daily_transactions(target_date_str: str = None):
    if target_date_str:
        try:
            target_date = datetime.strptime(target_date_str, "%d/%m/%Y").date()
        except ValueError:
            return None # Invalid date format
    else:
        target_date = datetime.now(timezone.utc).date()
        
    start_of_day = datetime(target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc).isoformat()
    end_of_day = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59, 999999, tzinfo=timezone.utc).isoformat()
    
    response = supabase.table("transactions").select("*, items(name, price), branches(name)").gte("created_at", start_of_day).lte("created_at", end_of_day).execute()
    return response.data

def get_monthly_transactions(month_str: str = None):
    if month_str:
        try:
            target_date = datetime.strptime(month_str, "%m/%Y").date()
        except ValueError:
            return None # Invalid date format
    else:
        target_date = datetime.now(timezone.utc).date()
        
    start_of_month = datetime(target_date.year, target_date.month, 1, tzinfo=timezone.utc).isoformat()
    if target_date.month == 12:
        end_of_month = datetime(target_date.year + 1, 1, 1, tzinfo=timezone.utc) - timedelta(microseconds=1)
    else:
        end_of_month = datetime(target_date.year, target_date.month + 1, 1, tzinfo=timezone.utc) - timedelta(microseconds=1)
        
    end_of_month_iso = end_of_month.isoformat()
    
    response = supabase.table("transactions").select("*, items(name, price), branches(name)").gte("created_at", start_of_month).lte("created_at", end_of_month_iso).execute()
    return response.data

def get_all_inventory():
    response = supabase.table("inventory").select("*, items(barcode, name, price), branches(name)").execute()
    return response.data

def upsert_inventory(item_id: str, branch_id: str, quantity_change: int):
    # Fetch current
    current = get_inventory(item_id, branch_id)
    if current:
        new_quantity = current['quantity'] + quantity_change
        response = supabase.table("inventory").update({"quantity": new_quantity}).eq("item_id", item_id).eq("branch_id", branch_id).execute()
        return response.data[0] if response.data else None
    else:
        # If no previous inventory, create new
        data = {
            "item_id": item_id,
            "branch_id": branch_id,
            "quantity": quantity_change if quantity_change > 0 else 0
        }
        response = supabase.table("inventory").insert(data).execute()
        return response.data[0] if response.data else None

def get_all_branches():
    response = supabase.table("branches").select("*").execute()
    return response.data

def add_branch(name: str, location: str = ""):
    data = {"name": name, "location": location}
    response = supabase.table("branches").insert(data).execute()
    return response.data[0] if response.data else None

def set_user_branch(telegram_id: int, branch_id: str):
    response = supabase.table("users").update({"branch_id": branch_id}).eq("telegram_id", telegram_id).execute()
    return response.data[0] if response.data else None

def update_user_role(telegram_id: int, role: str):
    response = supabase.table("users").update({"role": role}).eq("telegram_id", telegram_id).execute()
    return response.data[0] if response.data else None

def search_item(query: str):
    response = supabase.table("items").select("*").or_(f"name.ilike.%{query}%,barcode.eq.{query}").execute()
    return response.data

def get_owners():
    response = supabase.table("users").select("telegram_id").eq("role", "owner").execute()
    return [user['telegram_id'] for user in response.data] if response.data else []

def get_transaction(txn_id: str):
    response = supabase.table("transactions").select("*").eq("id", txn_id).execute()
    return response.data[0] if response.data else None

def update_transaction_status(txn_id: str, status: str):
    response = supabase.table("transactions").update({"status": status}).eq("id", txn_id).execute()
    return response.data[0] if response.data else None

def check_nearby_branches(item_id: str, exclude_branch_id: str):
    response = supabase.table("inventory").select("*, branches(name)").eq("item_id", item_id).gt("quantity", 0).neq("branch_id", exclude_branch_id).execute()
    return response.data

def report_damage(item_id: str, branch_id: str, user_id: int, quantity: int, photo_file_id: str):
    data = {
        "item_id": item_id,
        "branch_id": branch_id,
        "user_id": user_id,
        "quantity": quantity,
        "photo_file_id": photo_file_id
    }
    response = supabase.table("defect_logs").insert(data).execute()
    return response.data[0] if response.data else None
