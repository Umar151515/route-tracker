from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from core.managers import ConfigManager


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