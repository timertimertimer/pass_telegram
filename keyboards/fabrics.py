from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class InlineCallbacks(CallbackData, prefix='path'):
    action: str


def get_inline_buttons(buttons: list[str] | str, adjust_num: int = 1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if isinstance(buttons, list):
        [builder.button(text=text, callback_data=InlineCallbacks(action=text)) for text in buttons]
    else:
        builder.button(text=buttons, callback_data=InlineCallbacks(action=buttons))
    builder.adjust(adjust_num)
    return builder.as_markup()
