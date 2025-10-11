from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from core.managers import UserManager
from core.managers import BusStopsManager
from core.managers import ConfigManager
from core.managers import GoogleSheetsManager
from utils.app import send_message, edit_message
from ..keyboards import get_stops_keyboard
from ..filters import driver_filter


router = Router()

@router.message(Command("delete_last_entry"), driver_filter())
@router.message(F.text == "🗑️ Удалить последнюю запись", driver_filter())
async def delete_last_entry(message: Message, sheets_manager: GoogleSheetsManager):
    user_id = message.from_user.id
    
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

@router.message(lambda message: message.text.isdigit(), driver_filter())
async def register_passengers(
    message: Message, 
    user_manager: UserManager,
    bus_stops_manager: BusStopsManager,
):
    user_id = message.from_user.id
    
    try:
        passenger_count = int(message.text)
    except ValueError:
        await send_message(message, "❌ Пожалуйста, введите только число пассажиров.", True)
        return

    if passenger_count < 0 or passenger_count > 200:
        await send_message(message, "❌ Количество пассажиров должно быть от 0 до 200.", True)
        return
    
    try:
        bus_number = await user_manager.get_parameters(user_id=user_id, get_bus_number=True)
        
        if not bus_number:
            await send_message(
                message,
                "❌ У вас не назначен автобус. Обратитесь к администратору.",
                reply=True
            )
            ConfigManager.log.logger.warning(f"⚠️ У пользователя ID {user_id} не назначен автобус")
            return
        
        if not await bus_stops_manager.bus_exists(bus_number=bus_number):
            await send_message(
                message,
                f"❌ Автобус '{bus_number}' не существует в системе. Обратитесь к администратору.",
                reply=True
            )
            ConfigManager.log.logger.error(f"⚠️ Автобус '{bus_number}' пользователя ID {user_id} не существует в системе")
            return

        stops = await bus_stops_manager.get_stops(bus_number=bus_number, get_stop_id=True)
        if not stops:
            await send_message(
                message,
                f"❌ Для автобуса '{bus_number}' не назначены остановки. Обратитесь к администратору.",
                reply=True
            )
            ConfigManager.log.logger.error(f"⚠️ У автобуса '{bus_number}' пользователя ID {user_id} нет остановок")
            return

    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при получении данных пользователя ID {user_id}")
        await send_message(
            message,
            "❌ Произошла ошибка при проверке данных. Обратитесь к администратору.",
            reply=True
        )
        return

    try:
        await send_message(
            message,
            "🛑 Выберите остановку:",
            reply=True,
            reply_markup=await get_stops_keyboard(
                bus_number,
                passenger_count
            )
        )
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при создании клавиатуры остановок для пользователя ID {user_id}")
        await send_message(message, "❌ Произошла ошибка при загрузке остановок.", reply=True)

@router.callback_query(F.data.startswith("register_passengers_"), driver_filter())
async def handle_register_passengers(
    callback: CallbackQuery, 
    user_manager: UserManager,
    bus_stops_manager: BusStopsManager, 
    sheets_manager: GoogleSheetsManager
):
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