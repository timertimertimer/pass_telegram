from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class InlineCallbacks(CallbackData, prefix='social'):
    action: str
    
    
def get_inline_buttons(buttons: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    [builder.button(text=text, callback_data=InlineCallbacks(action=action)) for text, action in buttons[:-1]]
    builder.button(text=buttons[-1][0], callback_data=InlineCallbacks(action=buttons[-1][1]))
    builder.adjust(3)
    return builder.as_markup()