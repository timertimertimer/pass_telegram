from contextlib import suppress
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest

from keyboards import fabrics
import data

router = Router()


@router.callback_query(fabrics.InlineCallbacks.filter())
async def callback_query_handler(call: CallbackQuery, callback_data: fabrics.InlineCallbacks) -> None:
    user_path = callback_data.action
    with suppress(TelegramBadRequest):
        await call.message.edit_text('Choose', reply_markup=fabrics.get_inline_buttons(data.ls(user_path)))
