from aiogram.fsm.state import StatesGroup, State


class AdminSheetsStates(StatesGroup):
    waiting_for_days_to_delete = State()
    waiting_for_days_to_get = State()
    confirm_delete = State()