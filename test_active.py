import asyncio
from bot.database import supabase_client
from bot.handlers.owner_handlers import get_delete_multi_keyboard

async def main():
    items = supabase_client.get_all_active_items()
    print(f"Active items count: {len(items)}")
    for item in items:
        print(item['name'], item['is_active'])

if __name__ == "__main__":
    asyncio.run(main())
