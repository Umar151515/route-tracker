from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from core.managers import ConfigManager
from utils.app import send_message
from ....keyboards.admin import app_config_keyboard
from ....filters import admin_filter


router = Router()

@router.message(F.text == "📱 Настройки приложения", admin_filter())
async def sheets_settings(message: Message):
    await send_message(message, "📱 Панель управления настройки приложения", reply_markup=app_config_keyboard)

@router.callback_query(F.data == "app_config:get", admin_filter())
async def cb_get_app_config(query: CallbackQuery):
    try:
        config_text = "⚙️ Текущие настройки приложения:\n\n"
        
        for key, value in ConfigManager.app.config.items():
            config_text += f"{key}: {value}\n"
        
        await query.message.edit_text(
            config_text,
            parse_mode=None
        )
        
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при получении конфигурации приложения")
        await query.message.edit_text("❌ **Ошибка!** Не удалось загрузить конфигурацию приложения.")