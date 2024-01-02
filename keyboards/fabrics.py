from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class InlineCallbacks(CallbackData, prefix='social'):
    action: str


def get_inline_buttons(buttons: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    [builder.button(text=text, callback_data=InlineCallbacks(action=text)) for text in buttons]
    builder.adjust(1)
    return builder.as_markup()
