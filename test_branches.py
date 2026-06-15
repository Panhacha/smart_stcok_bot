import asyncio
from bot.database import supabase_client

async def main():
    branches = supabase_client.get_all_branches()
    print("Branches:", branches)

if __name__ == "__main__":
    asyncio.run(main())
