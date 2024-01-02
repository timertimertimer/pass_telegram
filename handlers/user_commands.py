from aiogram import Router
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import data
from utils import Pass
from keyboards import fabrics

router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        f'Hello <b>{message.from_user.full_name}</b>',
        reply_markup=fabrics.get_inline_buttons(data.ls())
    )


@router.message(Command('get'))  # /get path
async def get(message: Message, command: CommandObject) -> None:
    user_path = command.args
    password = data.decrypt(user_path)
    password[0] = f'<code>{password[0]}</code>'
    await message.answer('\n'.join(password))


@router.message(Command('ls'))  # /ls [path]
async def ls(message: Message, command: CommandObject) -> None:
    user_path = command.args
    try:
        structure = '\n'.join(data.ls(user_path))
    except FileNotFoundError:
        await message.reply('No such file or directory')
        return
    if len(structure) > 4095:
        for x in range(0, len(structure), 4095):
            await message.answer(structure[x:x + 4095])
    else:
        await message.answer(structure)


@router.message(Command('generate'))  # /generate path [-n length]
async def generate(message: Message, command: CommandObject) -> None:
    args = command.args.split()
    user_path = args[0]
    try:
        match len(args):
            case 1:
                password = data.generate(user_path)
            case 3:  # [-n num]
                length = int(args[2])
                password = data.generate(user_path, length)
            case _:
                await message.reply('/generate path [-n length]')
                return
    except FileNotFoundError:
        await message.reply('No such file or directory')
        return
    await message.answer(f'<code>{password}</code>')


@router.message(Command('insert'))  # /insert path (password | -m)
async def insert(message: Message, command: CommandObject, state: FSMContext) -> None:
    args = command.args.split()
    user_path = args[0]
    if len(args) != 2:
        await message.answer('/insert path (password | -m)')
        return
    match args[2]:
        case '-m':
            await message.answer('Введите строки')
            await state.set_data({'user_path': user_path})
            await state.set_state(Pass.insert)
        case _:
            if data.insert(user_path, args[1]):
                await message.reply('Успешно добавлено')


@router.message(Pass.insert)
async def insert_strings(message: Message, state: FSMContext):
    password = message.text
    user_data = await state.get_data()
    if data.insert(user_data['user_path'], password):
        await message.reply('Успешно добавлено')
    await state.clear()
