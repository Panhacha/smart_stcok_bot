import json
from bot.database import supabase_client

def main():
    items = supabase_client.get_all_inventory()
    with open('test_supabase.json', 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
