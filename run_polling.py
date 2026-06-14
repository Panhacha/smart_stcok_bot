import asyncio
import logging
from bot.main import bot, dp

async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting bot in polling mode...")
    # Delete webhook to ensure polling works
    await bot.delete_webhook(drop_pending_updates=True)
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
