from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


user_settings_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👤 Найти пользователя", callback_data="user:get_info")],
    [InlineKeyboardButton(text="👥 Показать всех пользователей", callback_data="user:get_all")],
    [InlineKeyboardButton(text="✏️ Редактировать пользователя", callback_data="user:edit")],
    [InlineKeyboardButton(text="➕ Добавить пользователя", callback_data="user:add")],
    [InlineKeyboardButton(text="🗑️ Удалить пользователя", callback_data="user:delete")]
])

user_filters_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👨‍💻 Показать всех", callback_data="user:get_all:all")],
    [InlineKeyboardButton(text="🎭 Отфильтровать по роли", callback_data="user:get_all:by_role_menu")],
    [InlineKeyboardButton(text="🚌 Отфильтровать по автобусу", callback_data="user:get_all:by_bus")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="user:settings")]
])

user_roles_filter_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🚛 Водители", callback_data="user:get_all:by_role:driver")],
    [InlineKeyboardButton(text="👑 Администраторы", callback_data="user:get_all:by_role:admin")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="user:get_all")]
])

user_edit_start_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Начать редактирование", callback_data="user:edit:start")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="user:settings")]
])

user_add_role_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🚛 Водитель", callback_data="user:add:role:driver")],
    [InlineKeyboardButton(text="👑 Администратор", callback_data="user:add:role:admin")],
    [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
])

user_delete_confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да, удалить", callback_data="user:delete:confirm")],
    [InlineKeyboardButton(text="❌ Нет, отменить", callback_data="user:delete:cancel")]
])

def get_user_edit_fields_keyboard(role: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Изменить имя", callback_data="user:edit:field:name")],
        [InlineKeyboardButton(text="Изменить телефон", callback_data="user:edit:field:phone")]
    ]
    if role == 'driver':
        buttons.append([InlineKeyboardButton(text="Изменить номер автобуса", callback_data="user:edit:field:bus_number")])
    
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)