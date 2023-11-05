from typing import Callable, Awaitable, Any, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

class CheckAdminMiddleware(BaseMiddleware):
    def __init__(self, admins: int | list[int]=[222215932]) -> None:
        if isinstance(admins, int):
            admins = [admins]
        self.admins = admins

    async def __call__(
        self, 
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        
        if event.from_user.id in self.admins:
            return await handler(event, data)
        return