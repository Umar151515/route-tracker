from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


logs_settings_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📋 Показать логи", callback_data="logs:show")],
    [InlineKeyboardButton(text="🗑 Очистить логи", callback_data="logs:clear")],
    [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
])