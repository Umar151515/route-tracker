from aiogram import F, Router
from aiogram.types import CallbackQuery

from core.managers import ConfigManager
from utils.app import edit_message
from ....filters import admin_filter


router = Router()

@router.callback_query(F.data == "logs:clear", admin_filter())
async def cb_clear_logs(query: CallbackQuery):
    try:
        ConfigManager.log.clear_logs()
        ConfigManager.log.logger.info(f"Админ ID: {query.from_user.id} очистил логи")
        await edit_message(query.message, "✅ Лог-файл успешно очищен!")
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n Ошибка при очистке логов.")
        await edit_message(query.message, "❌ Произошла ошибка при очистке логов.")