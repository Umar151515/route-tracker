from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from core.managers import BusStopsManager, ConfigManager
from utils.text.processing import validate_bus_number
from utils.app import send_message, edit_message
from ....filters import admin_filter
from ....states.admin import AdminStopRemoveStates


router = Router()

@router.callback_query(F.data == "bus:remove_stop", admin_filter())
async def cb_remove_stop_start(
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

    await state.set_state(AdminStopRemoveStates.waiting_for_bus_number_for_remove_stop)
    await edit_message(
        query.message,
        "➖ Введите номер автобуса для удаления остановки:\n\n"
        f"**Доступные автобусы:** `{', '.join(f'`{number}`' for number in bus_numbers)}`\n\n"
        "*Для отмены отправьте `0`*"
    )

@router.message(AdminStopRemoveStates.waiting_for_bus_number_for_remove_stop, admin_filter())
async def handle_remove_stop_bus_number(message: Message, state: FSMContext, bus_stops_manager: BusStopsManager):
    bus_number = message.text.strip()

    if bus_number == "0":
        await state.clear()
        await send_message(message, "↩️ Удаление остановки отменено.")
        return

    if not validate_bus_number(bus_number):
        await send_message(message, "❌ Неверный формат номера автобуса. Попробуйте еще раз.")
        return

    try:
        if not await bus_stops_manager.bus_exists(bus_number=bus_number):
            await send_message(message, f"❌ Автобус с номером '{bus_number}' не найден. Попробуйте еще раз.")
            return

        stops = await bus_stops_manager.get_stops(bus_number=bus_number, get_stop_name=True, get_stop_order=True)
        if not stops:
            await send_message(message, f"❌ В автобусе '{bus_number}' нет остановок.")
            await state.clear()
            return

        stops_text = "\n".join([f"{stop[1]}. {stop[0]}" for stop in stops])
        await state.update_data(bus_number=bus_number)
        await state.set_state(AdminStopRemoveStates.waiting_for_stop_order_for_remove)
        await send_message(
            message,
            f"🛑 Остановки автобуса {bus_number}:\n{stops_text}\n\n"
            "➖ Введите порядковый номер остановки для удаления:\n\n"
            "*Для отмены отправьте `0`*"
        )
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при получении остановок автобуса {bus_number}")
        await send_message(message, "❌ Произошла ошибка при получении остановок.")
        await state.clear()

@router.message(AdminStopRemoveStates.waiting_for_stop_order_for_remove, admin_filter())
async def handle_remove_stop_order(message: Message, state: FSMContext, bus_stops_manager: BusStopsManager):
    data = await state.get_data()
    bus_number = data.get('bus_number')
    stop_order_str = message.text.strip()

    if stop_order_str == "0":
        await state.clear()
        await send_message(message, "↩️ Удаление остановки отменено.")
        return

    try:
        max_stop_order = len(await bus_stops_manager.get_stops(bus_number=bus_number, get_stop_id=True))
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при получении остановок автобуса {bus_number}")
        await send_message(message, "❌ Ошибка при получении остановок автобуса.")
        await state.clear()
        return

    if stop_order_str.isdigit():
        stop_order = int(stop_order_str)
        if stop_order <= 0:
            await send_message(message, "❌ Порядковый номер должен быть положительным числом. Попробуйте еще раз.")
            return
        elif stop_order > max_stop_order:
            await send_message(message, "❌ Нет такой остановки. Попробуйте еще раз.")
            return
    else:
        await send_message(message, "❌ Неверный формат порядкового номера. Попробуйте еще раз.")
        return

    try:
        stops = await bus_stops_manager.get_stops(bus_number=bus_number, get_stop_name=True, get_stop_order=True)
        stop_name = None
        for stop in stops:
            if stop[1] == stop_order:
                stop_name = stop[0]
                break
        
        await bus_stops_manager.delete_stop(bus_number=bus_number, stop_order=stop_order)
        
        ConfigManager.log.logger.info(f"Администратор ID - {message.from_user.id} удалил остановку '{stop_name}' (порядок: {stop_order}) из автобуса {bus_number}")
        
        await send_message(message, f"✅ Остановка под номером {stop_order} успешно удалена из автобуса '{bus_number}'!")
        await state.clear()
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при удалении остановки из автобуса '{bus_number}' по порядку {stop_order}.")
        await send_message(message, "❌ Произошла ошибка при удалении остановки.")
        await state.clear()