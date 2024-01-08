from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from pathlib import Path

from handlers.user_commands import add_password_handler
from keyboards import fabrics
import data
from utils import Pass, PASSWORD_CMDS, FOLDER_CMDS, show_generate_message

router = Router()


@router.callback_query(
    Pass.selecting,
    fabrics.InlineCallbacks.filter(F.action.endswith('/'))
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
    text = f'<b>{str(current_path.relative_to(data.password_store))}\nChoose</b>'
    if current_path != data.password_store:
        buttons = data.ls(current_path) + FOLDER_CMDS + ['Back']
    else:  # main menu
        buttons = data.ls() + FOLDER_CMDS
    reply_markup = fabrics.get_inline_buttons(buttons)
    await call.message.edit_text(text=text, reply_markup=reply_markup)
    await state.set_state(Pass.selecting)


@router.callback_query(
    Pass.selecting,
    fabrics.InlineCallbacks.filter(~F.action.endswith('/') & F.action.not_in(PASSWORD_CMDS + FOLDER_CMDS + ['Back']))
)
async def cat_callback(call: CallbackQuery, callback_data: fabrics.InlineCallbacks, state: FSMContext) -> None:
    state_data = await state.get_data()
    current_path: Path = state_data['current_path']
    password_path = current_path / callback_data.action
    await call.message.edit_text(
        text=f"{password_path.relative_to(data.password_store)}\n{data.decrypt(password_path)}",
        reply_markup=fabrics.get_inline_buttons(PASSWORD_CMDS + ['Back']),
        parse_mode=None
    )
    await state.update_data(current_path=password_path)


@router.callback_query(
    Pass.selecting,
    fabrics.InlineCallbacks.filter(F.action == 'Add')
)
async def add_callback(call: CallbackQuery, callback_data: fabrics.InlineCallbacks, state: FSMContext) -> None:
    await state.update_data(dialog_message=call.message)
    state_data = await state.get_data()
    current_path: Path = state_data['current_path']
    await call.message.edit_text(
        text=f'<b>{callback_data.action}\nWrite new creds for current path '
             f'{str(current_path.relative_to(data.password_store))} '
             f'(1st line - login (path + login), then - password and additional data)</b>',
        reply_markup=fabrics.get_inline_buttons('Back')
    )
    await state.set_state(Pass.add)


@router.callback_query(
    Pass.selecting,
    fabrics.InlineCallbacks.filter(F.action == 'Generate')
)
async def generate_callback(call: CallbackQuery, callback_data: fabrics.InlineCallbacks, state: FSMContext) -> None:
    await state.update_data(dialog_message=call.message)
    state_data = await state.get_data()
    current_path: Path = state_data['current_path']
    await call.message.edit_text(
        text=f'<b>{callback_data.action}\nWrite login (path + login) for current path '
             f'{str(current_path.relative_to(data.password_store))}</b>',
        reply_markup=fabrics.get_inline_buttons('Back')
    )
    await state.set_state(Pass.generate_input)


@router.callback_query(
    Pass.generate_settings,
    fabrics.InlineCallbacks.filter(F.action.in_(['extra symbols [ON]', 'extra symbols [OFF]']))
)
async def extra_symbols_callback(call: CallbackQuery, state: FSMContext) -> None:
    await show_generate_message(state)


@router.callback_query(
    Pass.generate_settings,
    fabrics.InlineCallbacks.filter(F.action == 'Generate')
)
async def generate_password_callback(call: CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    generated_password = data.generate_random_password(no_symbols=not state_data['extra_symbols'])
    await add_password_handler(state=state, login=state_data['login'], password=generated_password)


@router.callback_query(fabrics.InlineCallbacks.filter(F.action == 'Edit'))
async def edit_password_callback(call: CallbackQuery, callback_data: fabrics.InlineCallbacks,
                                 state: FSMContext) -> None:
    await state.update_data(dialog_message=call.message)
    state_data = await state.get_data()
    password_path: Path = state_data['current_path']
    await call.message.edit_text(
        text=f'<b>{callback_data.action}\nWrite new creds for current path '
             f'{str(password_path.relative_to(data.password_store))}</b>',
        reply_markup=fabrics.get_inline_buttons('Back')
    )
    await state.set_state(Pass.edit)


@router.callback_query(fabrics.InlineCallbacks.filter(F.action == 'Move'))
async def move_callback(call: CallbackQuery, callback_data: fabrics.InlineCallbacks, state: FSMContext) -> None:
    state_data = await state.get_data()
    password_path: Path = state_data['current_path']
    await call.message.edit_text(
        text=f'<b>{callback_data.action}\n</b>Write a new path for current path - '
             f'{str(password_path.relative_to(data.password_store))}</b>',
        reply_markup=fabrics.get_inline_buttons('Back')
    )
    await state.set_state(Pass.move)


@router.callback_query(fabrics.InlineCallbacks.filter(F.action == 'Delete'))
async def delete_callback(call: CallbackQuery, callback_data: fabrics.InlineCallbacks, state: FSMContext) -> None:
    state_data = await state.get_data()
    password_path: Path = state_data['current_path']
    await call.message.edit_text(
        text=f'<b>{callback_data.action}\nAre you sure you want to remove the password from the path '
             f'{str(password_path.relative_to(data.password_store))}?</b>',
        reply_markup=fabrics.get_inline_buttons(['Yes', 'No', 'Back'], adjust_num=2)
    )
    await state.set_state(Pass.delete)


@router.callback_query(
    Pass.delete,
    fabrics.InlineCallbacks.filter(F.action.in_(['Yes', 'No']))
)
async def delete_answer_callback(
        call: CallbackQuery,
        callback_data: fabrics.InlineCallbacks,
        state: FSMContext
) -> None:
    state_data = await state.get_data()
    password_path: Path = state_data['current_path']
    message = (f'Successfully deleted {str(password_path.relative_to(data.password_store))}\n'
               f'{data.delete(password_path)}') if callback_data.action == 'Yes' else 'Choose'
    await call.message.edit_text(text=message, reply_markup=fabrics.get_inline_buttons(data.ls() + FOLDER_CMDS))
    await state.update_data(current_path=data.password_store)
    await state.set_state(Pass.selecting)


@router.callback_query(
    Pass.selecting,
    fabrics.InlineCallbacks.filter(F.action == 'Back')
)
async def cd_parent_callback(call: CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    current_path: Path = state_data['current_path']
    if current_path != data.password_store:
        current_path = current_path.parent
    await call.message.edit_text(
        text=f'<b>{str(current_path.relative_to(data.password_store))}\nChoose</b>',
        reply_markup=fabrics.get_inline_buttons(
            data.ls(current_path) + (FOLDER_CMDS + ['Back'] if current_path != data.password_store else FOLDER_CMDS))
    )
    await state.update_data(current_path=current_path)


@router.callback_query(fabrics.InlineCallbacks.filter(F.action == 'Back'))
async def return_to_passwords_callback(call: CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    current_path: Path = state_data['current_path']
    await call.message.edit_text(
        text=f'<b>{str(current_path.relative_to(data.password_store))}\nChoose</b>',
        reply_markup=fabrics.get_inline_buttons(
            data.ls(current_path) + (FOLDER_CMDS + ['Back'] if current_path != data.password_store else FOLDER_CMDS))
    )
    await state.set_state(Pass.selecting)
