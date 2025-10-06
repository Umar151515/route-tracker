from aiogram import F, Router
from aiogram.types import Message, CallbackQuery

from core.managers import UserManager
from core.managers import BusStopsManager
from core.managers import ConfigManager
from core.managers import GoogleSheetsManager
from ..core.services import UserService
from ..utils import send_message, edit_message
from ..keyboards import get_stops_keyboard


router = Router()

@router.message(F.text == "🗑️ Удалить последнюю запись")
async def delete_last_entry(
    message: Message,
    user_service: UserService, 
    sheets_manager: GoogleSheetsManager
):
    user_id = message.from_user.id

    if not await user_service.check_user_role(user_id, "driver"):
        return
    
    if not await sheets_manager.was_last_registration_today(user_id):
        await send_message(message, f"❗ Дальше вы уже не можете удалять записи", None)
        return
    
    user_id = message.from_user.id

    try:
        await sheets_manager.delete_nth_last_driver_entry(user_id)
    except Exception as e:
        await send_message(message, f"❌ Произошла ошибка при удалении.", None)
        ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при удалении последней записи у пользователя ID {user_id}.")
        return
    
    await send_message(message, "Запись успешно удалена.")

@router.message(F.text)
async def register_passengers(
    message: Message, 
    user_manager: UserManager,
    bus_stops_manager: BusStopsManager, 
    user_service: UserService
):
    user_id = message.from_user.id
    
    if not await user_service.check_user_role(user_id, "driver"):
        return
    
    try:
        passenger_count = int(message.text)
    except ValueError:
        await send_message(message, "Пожалуйста, отправьте ТОЛЬКО КОЛИЧЕСТВО вошедших пассажиров числом.", True)
        return

    if passenger_count < 0 or passenger_count > 200:
        await send_message(message, "Введите реальное число вошедших пассажиров. Значение должно быть в пределах от 0 до 200.", True)
        return
    
    bus_number = await user_manager.get_parameters(user_id=user_id, get_bus_number=True)

    if not await bus_stops_manager.get_stops(bus_number=bus_number, get_stop_id=True):
        await send_message(
            message,
            f"❌ Кажется, для вашего автобуса ({bus_number}) не закреплены остановки. Это техническая ошибка. обратитесь к Администратору, чтобы он закрепил маршрут. Пока маршрут не закреплен, регистрация невозможна!",
            reply=True
        )
        ConfigManager.log.logger.critical(f"⚠️ У пользователя ID {user_id} нет закрепленных остановок. Регистрация пассажиров невозможна")
        return

    await send_message(
        message,
        "Выберите остановку",
        reply=True,
        reply_markup=await get_stops_keyboard(
            bus_stops_manager,
            bus_number,
            passenger_count
        )
    )

@router.callback_query(F.data.startswith("register_passengers_"))
async def handle_register_passengers(
    callback: CallbackQuery, 
    user_manager: UserManager,
    user_service: UserService, 
    bus_stops_manager: BusStopsManager, 
    sheets_manager: GoogleSheetsManager
):
    if not await user_service.check_user_role(callback.from_user.id, "driver"):
        return
    
    try:
        user_id = callback.from_user.id
        stop_id, passenger_count = map(int, callback.data.replace("register_passengers_", "").split("_"))
        driver_name, bus_number = await user_manager.get_parameters(user_id=user_id, get_name=True, get_bus_number=True)
        stop_name = await bus_stops_manager.get_stop(stop_id, get_stop_name=True)
    
    except Exception as e:
        await edit_message(callback.message, f"❌ Произошла ошибка. Остановка НЕ зарегистрирована. Попробуйте, пожалуйста, повторить ввод количества пассажиров.", None)
        ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка у пользователя {user_id} при получении данных в handle_register_passengers. Остановка НЕ зарегистрирована.")
        return

    try:
        await sheets_manager.add_row(
            user_id,
            driver_name,
            bus_number,
            stop_name,
            passenger_count
        )
    except Exception as e:
        await edit_message(callback.message, f"❌ Произошла ошибка. Не удалось сохранить данные об остановке. Произошел сбой при регистрации. Пожалуйста, повторите попытку ввода количества пассажиров.", None)
        ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при регистрации пассажиров у пользователя {driver_name}. Сбой при передаче/записи данных в таблицу.")
        return

    await edit_message(
        callback.message,
        f"Остановка {stop_name} зарегистрирована! Вошло {passenger_count} пассажиров."
    )