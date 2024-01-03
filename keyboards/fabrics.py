from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class InlineCallbacks(CallbackData, prefix='path'):
    action: str


def get_inline_buttons(buttons: list[str], adjust_num: int = 1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    [builder.button(text=text, callback_data=InlineCallbacks(action=text)) for text in buttons]
    builder.adjust(adjust_num)
    return builder.as_markup()
