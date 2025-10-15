from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ErrorEvent
from aiogram.fsm.context import FSMContext

from core.managers import UserManager
from core.managers import BusStopsManager
from core.managers import ConfigManager
from utils.app import send_message, edit_message
from ..keyboards import driver_main_keyboard, admin_main_keyboard
from ..filters import ExistsFilter


router = Router()

@router.message(CommandStart(), ExistsFilter())
async def cmd_start(message: Message, user_manager: UserManager):
    user_id = message.from_user.id
    
    try:
        role, name = await user_manager.get_parameters(user_id=user_id, get_role=True, get_name=True)
    except Exception as e:
        await send_message(message, f"❌ Произошла ошибка при получении данных.", None)
        ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при получении данных в user_information у пользователя ID {user_id}.")
        return
    if role == "driver":
        await send_message(
            message, 
            f"Добро пожаловать {name}!\n\n"
            "Вот что вы можете сделать:\n"
            "Чтобы удалить последнюю запись, используйте команду: /delete_last_entry\n"
            "Чтобы добавить новую запись, введите число от 0 до 200 и выберите остановку\n"
            "Чтобы посмотреть свои данные, используйте команду: /my_details\n"
            "Открыть главное меню: /menu\n",
            parse_mode=None
        )
    elif role == "admin":
        await send_message(
            message,
            f"Добро пожаловать {name}!\n\n"
            "Ваши админские возможности:\n"
            "Все настройки тут: /menu\n"
            "Чтобы посмотреть свои данные: /my_details\n"
            "Для быстрой настройки пользователя, введите его ID или номер телефона.",
            parse_mode=None
        )
    else:
        await send_message(message, f"❌ Роль не найдена сообщите это администратору.")
        ConfigManager.log.logger.critical(f"⚠️ У пользователя {name} не найдена роль {role}.")

@router.message(Command("my_details"), ExistsFilter())
@router.message(F.text == "👤 Мои данные", ExistsFilter())
async def user_information(message: Message, user_manager: UserManager, bus_stops_manager: BusStopsManager):
    user_id = message.from_user.id
    
    try:
        role, name, bus_number = await user_manager.get_parameters(
            user_id=user_id,
            get_role=True, 
            get_name=True, 
            get_bus_number=True
        )
        stop_names = []
        if bus_number and await bus_stops_manager.bus_exists(bus_number=bus_number):
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
                f"<b>Роль:</b> Админ\n"
                f"<b>Твой ID:</b> <code>{user_id}</code>"
            ),
            parse_mode=ParseMode.HTML
        )
    elif role == "driver":
        stops_list_str = "— " + "\n— ".join(stop_names) if stop_names else "Нет закрепленных остановок или автобус не существует. Cообщите это администратору!"
        if not stop_names:
            ConfigManager.log.logger.critical(f"⚠️ У пользователя {name} нет закрепленных остановок.")

        await send_message(
            message,
            "<b>🚌 Ваши рабочие данные:</b>\n\n"
            f"<b>Имя водителя:</b> {name}\n"
            f"<b>Номер автобуса:</b> {f"<code>{bus_number}</code>" if bus_number else "Автобус не закреплен"}\n"
            f"<b>Роль:</b> Водитель\n"
            f"<b>Твой ID:</b> <code>{user_id}</code>\n\n"
            
            f"<b>🚏 Закрепленные остановки:</b>\n"
            f"{stops_list_str}",
            parse_mode=ParseMode.HTML
        )
    else:
        await send_message(message, f"❌ Роль не найдена сообщите это администратору.")
        ConfigManager.log.logger.critical(f"⚠️ У пользователя {name} не найдена роль {role}.")

@router.message(Command("menu"), ExistsFilter())
async def get_contact(message: Message, user_manager: UserManager):
    user_id = message.from_user.id
    
    try:
        role, name = await user_manager.get_parameters(user_id=user_id, get_role=True, get_name=True)
    except Exception as e:
        await send_message(message, f"❌ Произошла ошибка при получении данных.", None)
        ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при получении данных в get_contact у пользователя ID {user_id}.")
        return

    if role == "admin":
        await send_message(message, "Главное меню администратора:", reply_markup=admin_main_keyboard)
    elif role == "driver":
        await send_message(message, "Главное меню водителя:", reply_markup=driver_main_keyboard)
    else:
        await send_message(message, f"❌ Роль не найдена сообщите это администратору.")
        ConfigManager.log.logger.critical(f"⚠️ У пользователя {name} не найдена роль {role}.")

@router.callback_query(F.data == "cancel", ExistsFilter())
async def cancel_action(event: Message | CallbackQuery, state: FSMContext):
    if state:
        await state.clear()
        
    if isinstance(event, CallbackQuery):
        await edit_message(event.message, "↩️ Операция отменена.")
    else:
        await send_message(event, "↩️ Операция отменена.")