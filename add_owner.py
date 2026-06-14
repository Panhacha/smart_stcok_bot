import asyncio
from bot.database import supabase_client

def main():
    print("Adding owner to database...")
    telegram_id = 7309869072
    
    # Check if user exists
    user = supabase_client.get_user(telegram_id)
    if user:
        print("User already exists!")
        return

    data = {
        "telegram_id": telegram_id,
        "role": "owner"
    }
    response = supabase_client.supabase.table("users").insert(data).execute()
    print("User added successfully:", response.data)

if __name__ == "__main__":
    main()
