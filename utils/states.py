from aiogram.fsm.state import StatesGroup, State


class Pass(StatesGroup):
    selecting = State()
    add = State()
    generate = State()
    generate_input = State()
