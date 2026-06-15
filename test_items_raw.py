import json
from bot.database import supabase_client

def main():
    response = supabase_client.supabase.table("items").select("*").execute()
    with open('test_items_raw.json', 'w', encoding='utf-8') as f:
        json.dump(response.data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
