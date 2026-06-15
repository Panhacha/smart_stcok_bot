import json
from bot.database import supabase_client

def main():
    item_id = "c9918928-5921-49d9-b16e-a70d0be1d98a"
    try:
        res = supabase_client.delete_item_by_id(item_id)
        print(f"Result: {res}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
