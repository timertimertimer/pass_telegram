import gnupg
import asyncio
import logging
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from filters.is_admin import IsAdmin

load_dotenv()

TOKEN = os.getenv("PASS_BOT_TOKEN")
dp = Dispatcher()

gpg = gnupg.GPG()
gpg.encoding = 'utf-8'

password_store = Path().home() / '.password-store'


@dp.message(CommandStart(), IsAdmin(222215932))
async def start(message: Message) -> None:
    await message.answer(f'Hello <b>{message.from_user.full_name}</b>')


@dp.message(IsAdmin(222215932))
async def echo(message: Message) -> None:
    user_path = message.text
    password = gpg.decrypt_file(str(password_store / (user_path + '.gpg')), passphrase=os.getenv('PASSPHRASE'))
    await message.answer(f'<span class="tg-spoiler">{str(password)}</span>')


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())