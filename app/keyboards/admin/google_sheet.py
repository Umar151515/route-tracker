from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


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

confirm_delete_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="✅ Подтвердить удаление", callback_data="sheets:confirm_delete:yes"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")
    ]
])