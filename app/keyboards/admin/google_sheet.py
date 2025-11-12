from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


sheets_settings_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🗑 Удалить данные за первые N дней", callback_data="sheets:delete_data")],
    [InlineKeyboardButton(text="📊 Получить данные за последние N дней", callback_data="sheets:get_data")],
    [InlineKeyboardButton(text="📈 Получить статистику", callback_data="sheets:get_stats")],
    [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
])

sheets_stats_date_filter_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📅 Конкретная дата", callback_data="sheets:stats_date_filter:specific")],
    [InlineKeyboardButton(text="🔢 Первые N дней", callback_data="sheets:stats_date_filter:first_days")],
    [InlineKeyboardButton(text="🔢 Последние N дней", callback_data="sheets:stats_date_filter:last_days")],
    [InlineKeyboardButton(text="📅 Диапазон дат", callback_data="sheets:stats_date_filter:date_range")],
    [InlineKeyboardButton(text="📊 Все данные", callback_data="sheets:stats_date_filter:all")],
    [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
])

sheets_stats_bus_filter_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🚌 Конкретные автобусы", callback_data="sheets:stats_bus_filter:specific")],
    [InlineKeyboardButton(text="🚌 Все автобусы", callback_data="sheets:stats_bus_filter:all")],
    [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
])

confirm_delete_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да, удалить", callback_data="sheets:confirm_delete:yes")],
    [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")]
])