import asyncio
from bot.database import supabase_client

async def main():
    print("Syncing missing items to inventory...")
    # Get all items
    items_res = supabase_client.supabase.table("items").select("*").execute()
    items = items_res.data
    
    # Get all branches
    branches_res = supabase_client.supabase.table("branches").select("*").execute()
    branches = branches_res.data
    
    count = 0
    for branch in branches:
        for item in items:
            # Check if inventory exists
            inv = supabase_client.get_inventory(item['id'], branch['id'])
            if not inv:
                # Insert with 0 stock
                supabase_client.upsert_inventory(item['id'], branch['id'], 0)
                count += 1
                print(f"Added item to branch (Item ID: {item['id']})")
                
    print(f"Done! Synced {count} missing records.")

if __name__ == '__main__':
    asyncio.run(main())
