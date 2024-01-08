from aiogram.fsm.state import StatesGroup, State


class Pass(StatesGroup):
    selecting = State()
    add = State()
    generate_settings = State()
    generate_input = State()
    edit = State()
    move = State()
    delete = State()
