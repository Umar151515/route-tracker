from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


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