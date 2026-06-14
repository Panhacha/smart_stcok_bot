from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from aiogram.fsm.context import FSMContext
import json
import os

def get_main_commands():
    filepath = os.path.join(os.path.dirname(__file__), "..", "ui", "keyboards.json")
    with open(filepath, "r", encoding="utf-8") as f:
        kb_data = json.load(f)
    
    commands = set()
    for menu in ["staff_menu", "owner_menu"]:
        for row in kb_data[menu]["keyboard"]:
            for btn in row:
                if "text" in btn:
                    commands.add(btn["text"])
    return commands

MAIN_COMMANDS = get_main_commands()

class CancelStateMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        
        if event.message and event.message.text:
            if event.message.text in MAIN_COMMANDS:
                state: FSMContext = data.get("state")
                if state:
                    await state.clear()
                    
        return await handler(event, data)
