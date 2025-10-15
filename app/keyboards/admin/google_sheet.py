from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


sheets_settings_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🗑 Удалить данные за N дней", callback_data="sheets:delete_data")],
    [InlineKeyboardButton(text="📊 Получить данные за N дней", callback_data="sheets:get_data")],
    [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
])

confirm_delete_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да, удалить", callback_data="sheets:confirm_delete:yes")],
    [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")]
])