from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from core.managers import BusStopsManager, ConfigManager
from utils.text.processing import validate_bus_number, validate_stop_name
from utils.app import send_message, edit_message
from ....states.admin import AdminBusAddStates
from ....filters import admin_filter


router = Router()

@router.callback_query(F.data == "bus:add", admin_filter())
async def cb_add_bus_start(query: CallbackQuery, state: FSMContext):
    await state.set_state(AdminBusAddStates.waiting_for_bus_number)
    await edit_message(
        query.message,
        "➕ **Создание нового автобуса**\n\n"
        "🚌 Введите номер автобуса:\n\n"
        "💡 Пример: 12 или 45А\n\n"
        "❌ Для отмены введите: 0"
    )

@router.message(AdminBusAddStates.waiting_for_bus_number, admin_filter())
async def handle_add_bus_number(
    message: Message, 
    state: FSMContext, 
    bus_stops_manager: BusStopsManager
):
    bus_number = message.text.strip()

    if bus_number == "0":
        await send_message(message, "❌ Создание автобуса отменено.")
        await state.clear()
        return

    if not validate_bus_number(bus_number):
        await send_message(message, "❌ Неверный формат номера автобуса. Попробуйте еще раз:")
        return

    try:
        if await bus_stops_manager.bus_exists(bus_number=bus_number):
            await send_message(message, f"❌ Автобус с номером '{bus_number}' уже существует. Введите другой номер:")
            return

    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при проверке автобуса {bus_number}")
        await send_message(message, "❌ Произошла ошибка при проверке автобуса. Попробуйте еще раз:")
        await state.clear()

    await state.update_data(bus_number=bus_number, stops=[])
    await state.set_state(AdminBusAddStates.waiting_for_stops)
    await send_message(
        message,
        f"✅ Номер автобуса '{bus_number}' принят!\n\n"
        "🛑 Теперь введите остановки через запятую:\n\n"
        "💡 **Пример:** Моссовет, 3-я гор больница, Вефа\n\n"
        "📝 **Правила ввода:**\n"
        "• Разделяйте остановки запятыми\n"
        "• Каждая остановка будет добавлена по порядку\n"
        "• Можно вводить несколько остановок за раз\n\n"
        "➡️ **Введите остановки или:**\n"
        "• '0' - завершить создание автобуса"
    )

@router.message(AdminBusAddStates.waiting_for_stops, admin_filter())
async def handle_add_bus_stops(
    message: Message, 
    state: FSMContext, 
    bus_stops_manager: BusStopsManager
):
    user_input = message.text.strip()
    data = await state.get_data()
    bus_number = data.get('bus_number')
    stops: list = data.get('stops', [])

    if user_input == "0":
        if not stops:
            await send_message(message, "❌ Нельзя создать автобус без остановок. Операция отменена.")
            await state.clear()
            return

        try:
            await bus_stops_manager.create_bus(bus_number)
            
            for stop_order, stop_name in enumerate(stops, 1):
                await bus_stops_manager.create_stop(
                    bus_number=bus_number, 
                    stop_name=stop_name.strip(), 
                    stop_order=stop_order
                )
        except Exception as e:
            ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при создании автобуса {bus_number} с остановками.")
            await send_message(message, "❌ Произошла ошибка при создании автобуса.")
            await state.clear()
            return
    
        stops_list = "\n".join([f"{i+1}. {stop}" for i, stop in enumerate(stops)])
        await send_message(
            message,
            f"✅ **Автобус успешно создан!**\n\n"
            f"🚌 **Номер автобуса:** {bus_number}\n"
            f"🛑 **Добавлено остановок:** {len(stops)}\n\n"
            f"**Список остановок:**\n{stops_list}"
        )
        await state.clear()

        return

    new_stops = [stop.strip() for stop in user_input.split(",") if stop.strip()]
    valid_stops = []
    invalid_stops = []

    for stop in new_stops:
        if validate_stop_name(stop):
            valid_stops.append(stop)
        else:
            invalid_stops.append(stop)

    stops.extend(valid_stops)
    await state.update_data(stops=stops)

    response_parts = []
    
    if valid_stops:
        response_parts.append(f"✅ Добавлено остановок: {len(valid_stops)}")
        if len(valid_stops) <= 5:
            response_parts.append("\n".join([f"• {stop}" for stop in valid_stops]))
    
    if invalid_stops:
        response_parts.append(f"❌ Некорректные названия ({len(invalid_stops)}):")
        response_parts.append("\n".join([f"• {stop}" for stop in invalid_stops]))
        response_parts.append("\n💡 Исправьте названия и введите их снова:")

    response_parts.append(f"\n📊 Всего остановок: {len(stops)}")
    
    if stops:
        current_stops = "\n".join([f"{i+1}. {stop}" for i, stop in enumerate(stops)])
        response_parts.append(f"\nТекущий маршрут:\n{current_stops}")

    response_parts.append(
        f"\n➡️ Продолжайте вводить остановки или:\n"
        f"• '0' - завершить создание автобуса\n"
        f"• 'отмена' - отменить создание"
    )

    await send_message(message, "\n".join(response_parts), parse_mode=None)