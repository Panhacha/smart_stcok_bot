import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

async def check_low_stock(bot: Bot, owner_id: int):
    logging.info("Checking for low stock...")
    # Stub implementation: Fetch from supabase items with stock < threshold
    # For now, it's just a placeholder to show where the logic goes
    pass

def setup_scheduler(bot: Bot, owner_id: int):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_low_stock, 'interval', hours=1, args=[bot, owner_id])
    scheduler.start()
    return scheduler
