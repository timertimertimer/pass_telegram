from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import data
from utils import Pass, FOLDER_CMDS
from keyboards import fabrics

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.set_state(Pass.selecting)
    await state.update_data(current_path=data.password_store)
    await message.answer(
        f'Hello <b>{message.from_user.full_name}</b>',
        reply_markup=fabrics.get_inline_buttons(data.ls() + FOLDER_CMDS)
    )
