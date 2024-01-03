from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from pathlib import Path

from keyboards import fabrics
import data
from utils import Pass, CMDS

router = Router()


@router.callback_query(
    Pass.selecting,
    fabrics.InlineCallbacks.filter((F.action.not_in(['Add', 'Generate'])) & ~F.action.endswith('.gpg'))
)
async def cd_callback(call: CallbackQuery, callback_data: fabrics.InlineCallbacks, state: FSMContext) -> None:
    await state.update_data(dialog_message=call.message)
    state_data = await state.get_data()
    current_path: Path = state_data['current_path']
    user_path = callback_data.action
    if user_path == 'Back' and current_path != data.password_store:
        current_path = current_path.parent
    else:
        current_path = current_path / user_path
    await state.update_data(current_path=current_path)
    text = '<b>Choose</b>'
    if current_path != data.password_store:
        buttons = data.ls(current_path) + CMDS
    else:  # main menu
        buttons = data.ls() + CMDS[:-1]  # without `Back`
    reply_markup = fabrics.get_inline_buttons(buttons)
    await call.message.edit_text(text=text, reply_markup=reply_markup)
    await state.set_state(Pass.selecting)


@router.callback_query(
    Pass.selecting,
    fabrics.InlineCallbacks.filter(F.action.endswith('.gpg'))
)
async def get_callback(call: CallbackQuery, callback_data: fabrics.InlineCallbacks, state: FSMContext) -> None:
    state_data = await state.get_data()
    current_path: Path = state_data['current_path']
    password_path = current_path / callback_data.action
    await call.message.edit_text(
        text=data.decrypt(password_path),
        reply_markup=fabrics.get_inline_buttons(data.ls()),
        parse_mode=None
    )
    await state.update_data(current_path=data.password_store)


@router.callback_query(
    Pass.selecting,
    fabrics.InlineCallbacks.filter(F.action == 'Add')
)
async def add_callback(call: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(dialog_message=call.message)
    state_data = await state.get_data()
    current_path: Path = state_data['current_path']
    await call.message.edit_text(
        text=f'<b>Введите данные для текущего пути "{str(current_path.relative_to(data.password_store))}" '
             f'(1-ая строка - логин, последующие - пароль и доп. данные)</b>')
    await state.set_state(Pass.add)


@router.message(Pass.add)
async def add_password_handler(
        state: FSMContext, message: Message = None,
        login: str = None, password: str = None) -> None:
    state_data = await state.get_data()
    current_path: Path = state_data['current_path']
    if not (login and password):
        login, password = message.text.split('\n', maxsplit=1)
        await message.delete()
    if data.insert(current_path / login, password):
        dialog_message: Message = state_data['dialog_message']
        await dialog_message.edit_text(
            text='<b>Успешно добавлено</b>',
            reply_markup=fabrics.get_inline_buttons(data.ls() + CMDS[:-1])
        )
    await state.update_data(current_path=data.password_store)
    await state.set_state(Pass.selecting)


@router.callback_query(
    Pass.selecting,
    fabrics.InlineCallbacks.filter(F.action == 'Generate')
)
async def generate_callback(call: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(dialog_message=call.message)
    state_data = await state.get_data()
    current_path: Path = state_data['current_path']
    await call.message.edit_text(
        text=f'<b>Введите логин для текущего пути "{str(current_path.relative_to(data.password_store))}"</b>')
    await state.set_state(Pass.generate_input)


async def show_generate_message(state: FSMContext) -> None:
    state_data = await state.get_data()
    dialog_message: Message = state_data['dialog_message']
    current_path: Path = state_data['current_path']
    extra_symbols: bool = state_data['extra_symbols']
    login: str = state_data['login']
    await dialog_message.edit_text(
        text=f'<b>Генератор 25 символов для текущего пути "{str(current_path.relative_to(data.password_store) / login)}"</b>',
        reply_markup=fabrics.get_inline_buttons(
            [f'extra symbols [{"ON" if extra_symbols else "OFF"}]', 'Generate'],
            adjust_num=2
        )
    )
    await state.update_data(extra_symbols=not extra_symbols)


@router.message(Pass.generate_input)
async def generate_input_handler(message: Message, state: FSMContext) -> None:
    await message.delete()
    await state.update_data(login=message.text.strip())
    await state.update_data(extra_symbols=True)
    await show_generate_message(state)
    await state.set_state(Pass.generate)


@router.callback_query(
    Pass.generate,
    fabrics.InlineCallbacks.filter(F.action.in_(['extra symbols [ON]', 'extra symbols [OFF]']))
)
async def extra_symbols_callback(call: CallbackQuery, state: FSMContext) -> None:
    await show_generate_message(state)


@router.callback_query(
    Pass.generate,
    fabrics.InlineCallbacks.filter(F.action == 'Generate')
)
async def generate_password_handler(call: CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    generated_password = data.generate_random_password(no_symbols=not state_data['extra_symbols'])
    await add_password_handler(state, login=state_data['login'], password=generated_password)
