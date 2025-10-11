from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from core.managers import BusStopsManager, ConfigManager
from utils.text.processing import validate_bus_number
from ....utils import send_message, edit_message
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
        "💡 Пример: 12 или 45А\n\n"
        f"**Доступные автобусы:** `{', '.join(f'`{number}`' for number in bus_numbers)}`"
    )

@router.message(AdminStopRemoveStates.waiting_for_bus_number_for_remove_stop, admin_filter())
async def handle_remove_stop_bus_number(message: Message, state: FSMContext, bus_stops_manager: BusStopsManager):
    bus_number = message.text.strip()

    if not validate_bus_number(bus_number):
        await send_message(message, "❌ Неверный формат номера автобуса.")
        await state.clear()
        return

    try:
        if not await bus_stops_manager.bus_exists(bus_number=bus_number):
            await send_message(message, f"❌ Автобус с номером '{bus_number}' не найден.")
            await state.clear()
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
            "➖ Введите порядковый номер остановки для удаления:"
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

    await state.clear()

    try:
        max_stop_order = len(await bus_stops_manager.get_stops(bus_number=bus_number, get_stop_id=True))
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при получении остановок автобуса {bus_number}")
        await send_message(message, "❌ Ошибка при получении остановок автобуса.")
        return

    if stop_order_str.isdigit():
        stop_order = int(stop_order_str)
        if stop_order <= 0:
            await send_message(message, "❌ Порядковый номер должен быть положительным числом.")
            return
        elif stop_order > max_stop_order:
            await send_message(message, "❌ Нет такой остановки.")
            return
    else:
        await send_message(message, "❌ Неверный формат порядкового номера.")

    try:
        await bus_stops_manager.delete_stop(bus_number=bus_number, stop_order=stop_order)
        await send_message(message, f"✅ Остановка под номером {stop_order} успешно удалена из автобуса '{bus_number}'!")
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при удалении остановки из автобуса '{bus_number}' по порядку {stop_order}.")
        await send_message(message, "❌ Произошла ошибка при удалении остановки.")