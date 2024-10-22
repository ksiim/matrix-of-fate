from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    birth_date = State()
