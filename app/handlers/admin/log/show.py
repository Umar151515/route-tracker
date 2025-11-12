from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile

from core.managers import ConfigManager
from utils.app import send_message, edit_message
from ....keyboards.admin import logs_settings_keyboard
from ....filters import admin_filter


router = Router()

@router.message(F.text == "🔑 Настройки логирования", admin_filter())
async def logs_settings(message: Message):
    await send_message(message, "🔑 Панель управления логами системы", reply_markup=logs_settings_keyboard)

@router.callback_query(F.data == "logs:show", admin_filter())
async def cb_show_logs(query: CallbackQuery):
    try:
        logs_content = ConfigManager.log.get_logs()
        
        if not logs_content:
            await edit_message(query.message, "📭 Лог-файл пуст.")
            return

        if len(logs_content) > 4000:
            try:
                log_file = FSInputFile(ConfigManager.log.log_file, filename="system_logs.txt")
                await query.message.answer_document(log_file, caption="📁 Лог-файл системы")
                await query.message.delete()
            except Exception as e:
                ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при отправке лог-файла.")
                await edit_message(query.message, "❌ Произошла ошибка при отправке лог-файла.")
        else:
            await edit_message(query.message, f"📋 Содержимое лог-файла:\n\n```\n{logs_content}\n```")
            
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при получении логов.")
        await edit_message(query.message, "❌ Произошла ошибка при получении логов.")

