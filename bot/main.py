import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH
from bot.handlers import base_handlers, staff_handlers, owner_handlers
from bot.middlewares.auth_middleware import AuthMiddleware
from bot.middlewares.cancel_state import CancelStateMiddleware

logging.basicConfig(level=logging.INFO)

# Initialize Bot and Dispatcher
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Register Middlewares
dp.update.middleware(CancelStateMiddleware())
dp.update.middleware(AuthMiddleware())

# Register Routers
dp.include_router(base_handlers.router)
dp.include_router(staff_handlers.router)
dp.include_router(owner_handlers.router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Set webhook on startup
    if BOT_TOKEN:
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != WEBHOOK_URL:
            await bot.set_webhook(url=WEBHOOK_URL)
            logging.info(f"Webhook set to {WEBHOOK_URL}")
            
        # Set bot commands
        commands = [
            types.BotCommand(command="start", description="ចាប់ផ្តើមប្រើប្រាស់ Bot / Start bot"),
            # You can add more commands here if you have them, e.g.,
            # types.BotCommand(command="help", description="ជំនួយ / Help")
        ]
        await bot.set_my_commands(commands)
        
    yield
    # Delete webhook on shutdown
    if BOT_TOKEN:
        await bot.delete_webhook()
        await bot.session.close()

app = FastAPI(lifespan=lifespan)

@app.post(WEBHOOK_PATH)
async def bot_webhook(request: Request):
    update_data = await request.json()
    update = types.Update(**update_data)
    await dp.feed_update(bot, update)
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Store Management Bot is running"}
