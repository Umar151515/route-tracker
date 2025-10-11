from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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