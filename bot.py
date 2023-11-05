import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode

from handlers import user_commands
from middlewares import CheckAdminMiddleware

load_dotenv()

TOKEN = os.getenv("PASS_BOT_TOKEN")
dp = Dispatcher()

async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
      
    await bot.delete_webhook(drop_pending_updates=True)
    
    dp.message.middleware(CheckAdminMiddleware())
    
    dp.include_routers(user_commands.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
