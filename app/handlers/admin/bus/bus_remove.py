from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from core.managers import BusStopsManager, ConfigManager
from utils.text.processing import validate_bus_number
from ....utils import send_message, edit_message
from ....states.admin import AdminBusRemoveStates
from ....filters import admin_filter


router = Router()

@router.callback_query(F.data == "bus:remove", admin_filter())
async def cb_remove_bus_start(
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

    await state.set_state(AdminBusRemoveStates.waiting_for_bus_number_for_remove)
    await edit_message(
        query.message,
        "🗑 Введите номер автобуса для удаления:\n\n"
        "💡 Пример: 12 или 45А\n\n"
        f"**Доступные автобусы:** `{', '.join(f'`{number}`' for number in bus_numbers)}`"
    )

@router.message(AdminBusRemoveStates.waiting_for_bus_number_for_remove, admin_filter())
async def handle_remove_bus(message: Message, state: FSMContext, bus_stops_manager: BusStopsManager):
    bus_number = message.text.strip()
    await state.clear()

    if not validate_bus_number(bus_number):
        await send_message(message, "❌ Неверный формат номера автобуса.")
        return

    try:
        if not await bus_stops_manager.bus_exists(bus_number=bus_number):
            await send_message(message, f"❌ Автобус с номером '{bus_number}' не найден.")
            return

        await bus_stops_manager.delete_bus(bus_number=bus_number)
        await send_message(message, f"✅ Автобус '{bus_number}' успешно удален!")
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при удалении автобуса {bus_number}.")
        await send_message(message, "❌ Произошла ошибка при удалении автобуса.")