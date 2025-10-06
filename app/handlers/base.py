from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from core.managers import UserManager
from core.managers import BusStopsManager
from core.managers import ConfigManager
from core.managers import GoogleSheetsManager
from ..core.services import UserService
from ..utils import send_message, edit_message
from ..keyboards import get_stops_keyboard


router = Router()

@router.message(F.text == "👤 Мои данные")
async def user_information(message: Message, user_service: UserService, user_manager: UserManager, bus_stops_manager: BusStopsManager):
    user_id = message.from_user.id

    if not await user_service.check_user_exists(user_id):
        return
    
    try:
        role, name, bus_number = await user_manager.get_parameters(
            user_id=user_id,
            get_role=True, 
            get_name=True, 
            get_bus_number=True
        )
        stop_names = await bus_stops_manager.get_stops(bus_number=bus_number, get_stop_name=True)
    except Exception as e:
        await send_message(message, f"❌ Произошла ошибка при получении данных.", None)
        ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при получении данных в user_information у пользователя ID {user_id}.")
        return

    if role == "admin":
        await send_message(
            message, 
            (
                "<b>⚙️ Данные Администратора:</b>\n\n"
                f"<b>Имя:</b> {name}\n"
                f"<b>Роль:</b> <tg-spoiler>Админ</tg-spoiler>\n"
                f"<b>Твой ID:</b> <code>{user_id}</code>"
            ),
            parse_mode=ParseMode.HTML
        )
    elif role == "driver":
        stops_list_str = "— " + "\n— ".join(stop_names) if stop_names else "Нет закрепленных остановок. Cообщите это администратору!"
        if not stop_names:
            ConfigManager.log.logger.critical(f"⚠️ У пользователя {name} нет закрепленных остановок.")

        await send_message(
            message, 
            (
                "<b>🚌 Ваши рабочие данные:</b>\n\n"
                f"<b>Имя водителя:</b> {name}\n"
                f"<b>Номер автобуса:</b> <code>{bus_number}</code>\n"
                f"<b>Роль:</b> Водитель\n"
                f"<b>Твой ID:</b> <code>{user_id}</code>\n\n"
                
                f"<b>🚏 Закрепленные остановки:</b>\n"
                f"{stops_list_str}"
            ), 
            parse_mode=ParseMode.HTML
        )
    else:
        await send_message(message, f"❌ Роль не найдена сообщите это администратору.")
        ConfigManager.log.logger.critical(f"⚠️ У пользователя {name} не найдена роль {role}.")