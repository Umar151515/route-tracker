from aiogram.fsm.state import StatesGroup, State


class AdminBusInfoStates(StatesGroup):
    waiting_for_bus_number = State()


class AdminBusAddStates(StatesGroup):
    waiting_for_bus_number_for_add = State()
    waiting_for_bus_number = State()
    waiting_for_stops = State()


class AdminBusRemoveStates(StatesGroup):
    waiting_for_bus_number_for_remove = State()


class AdminStopAddStates(StatesGroup):
    waiting_for_bus_number_for_add_stop = State()
    waiting_for_stop_name = State()
    waiting_for_stop_order = State()


class AdminStopRemoveStates(StatesGroup):
    waiting_for_bus_number_for_remove_stop = State()
    waiting_for_stop_order_for_remove = State()