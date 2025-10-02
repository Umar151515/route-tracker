

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from core.managers import ConfigManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.managers import BusStopsManager


def get_main_keyboard(search_enabled: bool = False) -> ReplyKeyboardMarkup:
    search_text = "🌐 Выключить поиск в интернете ✅" if search_enabled else "🌐 Включить поиск в интернете ❌"
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=search_text)],
            [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="👤 Мой аккаунт")],
            [KeyboardButton(text="🗑️ Очистить чат"), KeyboardButton(text="🔍 История чата")]
        ],
        resize_keyboard=True
    )
    return keyboard

driver_main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/delete_entry")]
    ],
    resize_keyboard=True
)

phone_number_keyboard = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(
            text="Поделиться моим номером телефона",
            request_contact=True
        )
    ]],
    resize_keyboard=True,
    one_time_keyboard=True
)

async def get_stops_keyboard(bus_stops_manager: BusStopsManager, bus_number: str, number_of_passengers: int) -> InlineKeyboardMarkup:
    
    stops = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=stop_name, 
                callback_data=f"register_passengers_{stop_id}_{number_of_passengers}"
            )
        ] for stop_id, stop_name in await bus_stops_manager.get_stops(bus_number, get_stop_id=True, get_stop_name=True)
    ])

    return stops