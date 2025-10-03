from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from core.managers import ConfigManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.managers import BusStopsManager


driver_main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/delete_entry")]
    ],
    resize_keyboard=True
)

async def get_stops_keyboard(bus_stops_manager: "BusStopsManager", bus_number: str, number_of_passengers: int) -> InlineKeyboardMarkup:
    
    stops = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=stop_name, 
                callback_data=f"register_passengers_{stop_id}_{number_of_passengers}"
            )
        ] for stop_id, stop_name in await bus_stops_manager.get_stops(bus_number, get_stop_id=True, get_stop_name=True)
    ])

    return stops