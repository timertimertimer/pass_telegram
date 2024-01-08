from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import data
from utils import Pass, FOLDER_CMDS, logger, show_generate_message
from keyboards import fabrics

from pathlib import Path

router = Router()


@router.message(Pass.add)
async def add_password_handler(
        message: Message = None, state: FSMContext = None,
        login: str = None, password: str = None) -> None:
    state_data = await state.get_data()
    current_path: Path = state_data['current_path']
    if not (login and password):
        try:
            login, password = message.text.split('\n', maxsplit=1)
            await message.delete()
        except Exception as e:
            logger.info(e)
            await message.delete()
            return
    path = current_path / login if login else current_path
    if data.insert(path, password):
        dialog_message: Message = state_data['dialog_message']
        await dialog_message.edit_text(
            text=f'<b>{str(path.relative_to(data.password_store))}\nSuccessfully added</b>',
            reply_markup=fabrics.get_inline_buttons(data.ls() + FOLDER_CMDS)
        )
    await state.update_data(current_path=data.password_store)
    await state.set_state(Pass.selecting)


@router.message(Pass.generate_input)
async def generate_input_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(login=message.text.strip())
    await message.delete()
    await state.update_data(extra_symbols=True)
    await show_generate_message(state)
    await state.set_state(Pass.generate_settings)


@router.message(Pass.edit)
async def edit_password_handler(message: Message, state: FSMContext) -> None:
    await message.delete()
    state_data = await state.get_data()
    password_path: Path = state_data['current_path']
    login = password_path.name
    password = message.text.strip()
    await add_password_handler(message=message, state=state, login=login, password=password)


@router.message(Pass.move)
async def move_handler(message: Message, state: FSMContext):
    # TODO: test
    await message.delete()
    state_data = await state.get_data()
    dialog_message: Message = state_data['dialog_message']
    password_path: Path = state_data['current_path']
    new_path = message.text.strip()
    ok, old_path, new_path = data.mv(password_path, new_path)
    if ok:
        await dialog_message.edit_text(
            text=f'<b>Successfully moved from {str(old_path.relative_to(data.password_store))} '
                 f'to {str(new_path.relative_to(data.password_store))}</b>',
            reply_markup=fabrics.get_inline_buttons(data.ls() + FOLDER_CMDS)
        )
        await state.set_state(Pass.selecting)
    else:
        await dialog_message.edit_text(
            text=f'<b>Move\n</b>Write a new path for current path - '
                 f'{str(password_path.relative_to(data.password_store))}</b>',
            reply_markup=fabrics.get_inline_buttons('Back')
        )
