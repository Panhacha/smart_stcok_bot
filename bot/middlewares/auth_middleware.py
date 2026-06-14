import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from bot.database import supabase_client
import asyncio

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        
        user_id = None
        if event.message:
            user_id = event.message.from_user.id
        elif event.callback_query:
            user_id = event.callback_query.from_user.id
            
        if user_id:
            try:
                # Call synchronous Supabase client via to_thread to avoid blocking event loop
                db_user = await asyncio.to_thread(supabase_client.get_user, user_id)
                if db_user:
                    data['user_role'] = db_user['role']
                    data['branch_id'] = db_user['branch_id']
                else:
                    data['user_role'] = 'unregistered'
                    data['branch_id'] = None
            except Exception as e:
                logging.error(f"Supabase error in AuthMiddleware: {e}")
                data['user_role'] = 'unregistered'
                data['branch_id'] = None
                
        return await handler(event, data)
