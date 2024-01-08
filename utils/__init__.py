from pathlib import Path

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import data
from keyboards import fabrics
from .states import Pass
from .logger import logger

FOLDER_CMDS = ['Add', 'Generate']
PASSWORD_CMDS = ['Edit', 'Move', 'Delete']


async def show_generate_message(state: FSMContext) -> None:
    state_data = await state.get_data()
    dialog_message: Message = state_data['dialog_message']
    current_path: Path = state_data['current_path']
    extra_symbols: bool = state_data['extra_symbols']
    login: str = state_data['login']
    await dialog_message.edit_text(
        text=f'<b>Random password in {str(current_path.relative_to(data.password_store) / login)}</b>',
        reply_markup=fabrics.get_inline_buttons(
            [f'extra symbols [{"ON" if extra_symbols else "OFF"}]', 'Generate', 'Back'],
            adjust_num=2
        )
    )
    await state.update_data(extra_symbols=not extra_symbols)
