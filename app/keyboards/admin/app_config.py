from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.managers import ConfigManager


app_config_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📊 Просмотр текущих настроек", callback_data="app_config:get")],
    [InlineKeyboardButton(text="⚙️ Изменить настройки", callback_data="app_config:set")],
    [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
])

def get_app_config_set_keyboard():
    keyboard = []
    
    for key in ConfigManager.app.keys.keys():
        keyboard.append([
            InlineKeyboardButton(
                text=f"{key} ({ConfigManager.app.keys[key].__name__})", 
                callback_data=f"app_config:set_key:{key}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(text="↩️ Отмена", callback_data="app_config:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

app_config_set_keyboard = get_app_config_set_keyboard()