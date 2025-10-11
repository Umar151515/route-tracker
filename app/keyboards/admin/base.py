from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from core.managers import ConfigManager


user_settings_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text="👤 Получить информацию о пользователе", 
        callback_data="user:get_info"
    )],
    [InlineKeyboardButton(
        text="👥 Получить всех пользователей", 
        callback_data="user:get_all"
    )],
    [InlineKeyboardButton(
        text="✏ Изменить данные пользователя", 
        callback_data="user:edit"
    )]
])

bus_settings_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text="🚌 Получить все автобусы", 
        callback_data="bus:get_all"
    )],
    [InlineKeyboardButton(
        text="ℹ️ Получить информацию о автобусе", 
        callback_data="bus:get_info"
    )],
    [InlineKeyboardButton(
        text="➕ Добавить остановку", 
        callback_data="bus:add_stop"
    )],
    [InlineKeyboardButton(
        text="➖ Удалить остановку", 
        callback_data="bus:remove_stop"
    )],
    [InlineKeyboardButton(
        text="➕ Добавить автобус", 
        callback_data="bus:add"
    )],
    [InlineKeyboardButton(
        text="🗑 Удалить автобус", 
        callback_data="bus:remove"
    )]
])

sheets_settings_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text="🗑 Удалить данные за N дней", 
        callback_data="sheets:delete_data"
    )],
    [InlineKeyboardButton(
        text="📊 Получить данные за N дней", 
        callback_data="sheets:get_data"
    )]
])


