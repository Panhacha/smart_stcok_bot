import asyncio
import logging
from bot.main import bot, dp

async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting bot in polling mode...")
    # Delete webhook to ensure polling works
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Set bot commands
    from aiogram import types
    commands = [
        types.BotCommand(command="start", description="ចាប់ផ្តើមប្រើប្រាស់ Bot / Start bot"),
        types.BotCommand(command="help", description="ជំនួយ / Help")
    ]
    await bot.set_my_commands(commands)
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
