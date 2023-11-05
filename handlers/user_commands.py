from aiogram import Router
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message

import data

router = Router()

@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(f'Hello <b>{message.from_user.full_name}</b>')


@router.message(Command('get_pass'))
async def get_pass(message: Message, command: CommandObject) -> None:
    user_path = command.args
    password = data.decrypt(user_path)
    password[0] = f'<code>{password[0]}</code>'
    await message.answer('\n'.join(password))
    
    
@router.message(Command('ls'))
async def ls(message: Message, command: CommandObject) -> None:
    user_path = command.args
    try:
        structure = '\n'.join(data.ls(user_path))
    except FileNotFoundError:
        await message.reply('No such file or directory')
        return
    if len(structure) > 4095:
        for x in range(0, len(structure), 4095):
            await message.answer(structure[x:x+4095])
    else:
        await message.answer(structure)

@router.message(Command('generate'))
async def generate(message: Message, command: CommandObject) -> None:
    ...

@router.message(Command('insert'))
async def insert(message: Message, command: CommandObject) -> None:
    ...