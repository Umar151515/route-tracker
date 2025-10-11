from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from core.managers import BusStopsManager, ConfigManager
from utils.text.processing import validate_bus_number, validate_stop_name
from utils.app import send_message, edit_message
from ....filters import admin_filter
from ....states.admin import AdminStopAddStates


router = Router()

@router.callback_query(F.data == "bus:add_stop", admin_filter())
async def cb_add_stop_start(
    query: CallbackQuery, 
    state: FSMContext, 
    bus_stops_manager: BusStopsManager
):
    try:
        bus_numbers = await bus_stops_manager.get_buses(get_bus_number=True)
        if not bus_numbers:
            await edit_message(query.message, "📭 В системе пока нет зарегистрированных автобусов.")
            return
    except Exception as e:
        bus_numbers = ["Ошибка при получении списка автобусов"]
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при получении списка автобусов.")

    await state.set_state(AdminStopAddStates.waiting_for_bus_number_for_add_stop)
    await edit_message(
        query.message,
        "➕ Введите номер автобуса для добавления остановки:\n\n"
        "💡 Пример: 12 или 45А\n\n"
        f"**Доступные автобусы:** `{', '.join(f'`{number}`' for number in bus_numbers)}`"
    )

@router.message(AdminStopAddStates.waiting_for_bus_number_for_add_stop, admin_filter())
async def handle_add_stop_bus_number(message: Message, state: FSMContext, bus_stops_manager: BusStopsManager):
    bus_number = message.text.strip()

    if not validate_bus_number(bus_number):
        await send_message(message, "❌ Неверный формат номера автобуса.")
        return

    try:
        if not await bus_stops_manager.bus_exists(bus_number=bus_number):
            await send_message(message, f"❌ Автобус с номером '{bus_number}' не найден.")
            return
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при проверке автобуса {bus_number}.")
        await send_message(message, "❌ Произошла ошибка при проверке автобуса.")
        await state.clear()

    await state.update_data(bus_number=bus_number)
    await state.set_state(AdminStopAddStates.waiting_for_stop_name)
    await send_message(message, "🛑 Введите название остановки.")

@router.message(AdminStopAddStates.waiting_for_stop_name, admin_filter())
async def handle_add_stop_name(
    message: Message,
    state: FSMContext,
    bus_stops_manager: BusStopsManager
):
    stop_name = message.text.strip()
    data = await state.get_data()

    if not validate_stop_name(stop_name):
        await send_message(message, "❌ Неверный формат названия остановки.")
        await state.clear()
        return
    
    try:
        stops = await bus_stops_manager.get_stops(bus_number=data.get('bus_number'), get_stop_name=True)
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при получении списка остановок для автобуса: {data.get('bus_number')}.")
        stops = ["Ошибка при получении списка остановок"]

    stops_list = "\n".join([f"{i+1}. {stop}" for i, stop in enumerate(stops)])

    await state.update_data(stop_name=stop_name)
    await state.set_state(AdminStopAddStates.waiting_for_stop_order)
    await send_message(
        message,
        "🔢 Введи номер остановки для вставки (или 0, чтобы вставить в конец):\n"
        "💡 Пример: 1 (для первой) или 0 (в конец)\n\n"
        f"Остановки: \n{stops_list}"
    )

@router.message(AdminStopAddStates.waiting_for_stop_order, admin_filter())
async def handle_add_stop_order(message: Message, state: FSMContext, bus_stops_manager: BusStopsManager):
    data = await state.get_data()
    bus_number = data.get('bus_number')
    stop_name = data.get('stop_name')
    stop_order_str = message.text.strip()

    await state.clear()

    if stop_order_str == '0':
        stop_order = None
    elif stop_order_str.isdigit():
        stop_order = int(stop_order_str)
        if stop_order <= 0:
            await send_message(message, "❌ Порядковый номер должен быть положительным числом.")
            return
    else:
        await send_message(message, "❌ Неверный формат порядкового номера.")
        return

    try:
        await bus_stops_manager.create_stop(bus_number=bus_number, stop_name=stop_name, stop_order=stop_order)
        order_text = "в конец" if stop_order is None else f"под номером {stop_order}"
        await send_message(message, f"✅ Остановка '{stop_name}' успешно добавлена в автобус '{bus_number}' {order_text}!")
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при добавлении остановки '{stop_name}' в автобус '{bus_number}'.")
        await send_message(message, "❌ Произошла ошибка при добавлении остановки.")