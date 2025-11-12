from aiogram.fsm.state import State, StatesGroup


class AdminAppConfigStates(StatesGroup):
    waiting_for_config_key = State()
    waiting_for_config_value = State()