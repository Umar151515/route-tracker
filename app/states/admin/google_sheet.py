from aiogram.fsm.state import State, StatesGroup


class AdminSheetsStates(StatesGroup):
    waiting_for_days_to_get = State()
    
    waiting_for_days_to_delete = State()
    confirm_delete = State()
    
    waiting_for_stats_date_filter_type = State()
    waiting_for_stats_specific_date = State()
    waiting_for_stats_days_count = State()
    waiting_for_stats_start_date = State()
    waiting_for_stats_end_date = State()
    waiting_for_stats_bus_filter = State()
    waiting_for_stats_bus_numbers = State()