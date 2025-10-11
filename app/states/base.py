from aiogram.fsm.state import StatesGroup, State


class AdminUserStates(StatesGroup):
    waiting_for_bus_filter = State()
    waiting_for_identifier = State()


class AdminUserEditStates(StatesGroup):
    waiting_for_identifier = State()
    waiting_for_field = State()
    waiting_for_new_value = State()


class AdminUserAddStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_name = State()
    waiting_for_role = State()
    waiting_for_bus_number = State()


class AdminUserDeleteStates(StatesGroup):
    waiting_for_identifier = State()