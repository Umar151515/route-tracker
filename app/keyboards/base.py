from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from core.managers import ConfigManager
from core.managers import BusStopsManager


driver_main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🗑️ Удалить последнюю запись")],
        [KeyboardButton(text="👤 Мои данные")]
    ],
    resize_keyboard=True
)

admin_main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👥 Настройки пользователей")],
        [KeyboardButton(text="🚌 Настройки автобусов")],
        [KeyboardButton(text="📄 Настройки гугл таблицы")],
        [KeyboardButton(text="🔑 Настройки логирования")],
        [KeyboardButton(text="👤 Мои данные")]
    ],
    resize_keyboard=True
)

async def get_stops_keyboard(bus_stops_manager: BusStopsManager, bus_number: str, passenger_count: int) -> InlineKeyboardMarkup:
    
    stops = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=stop_name, 
                callback_data=f"register_passengers_{stop_id}_{passenger_count}"
            )
        ] for stop_id, stop_name in await bus_stops_manager.get_stops(bus_number, get_stop_id=True, get_stop_name=True)
    ])

    return stops