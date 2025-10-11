from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from core.managers import BusStopsManager, ConfigManager
from utils.text.processing import validate_bus_number
from utils.app import send_message, edit_message
from ....keyboards.admin import bus_settings_keyboard
from ....states.admin import AdminBusInfoStates
from ....filters import admin_filter


router = Router()

@router.message(F.text == "🚌 Настройки автобусов", admin_filter())
async def bus_settings(message: Message):
    await send_message(message, "🔧 Панель управления автобусами и остановками", reply_markup=bus_settings_keyboard)

@router.callback_query(F.data == "bus:get_all", admin_filter())
async def cb_get_all_buses(query: CallbackQuery, bus_stops_manager: BusStopsManager):
    try:
        buses = await bus_stops_manager.get_buses(get_bus_number=True)
        if not buses:
            await edit_message(query.message, "❌ В системе нет автобусов.")
            return
        
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при получении списка автобусов.")
        await edit_message(query.message, "❌ Произошла ошибка при получении списка автобусов.")

    text_parts = [f"Всего автобусов: {len(buses)}:"]
        
    for bus in buses:
        try:
            stops = await bus_stops_manager.get_stops(
                bus_number=bus, 
                get_stop_name=True, 
                get_stop_order=True
            )
            
            if stops:
                stops_list = [f"  {stop[1]}. {stop[0]}" for stop in stops]
                stops_text = "\n".join(stops_list)
                text_parts.append(f"\n\n🚌 Автобус {bus}:\n🛑 Остановки:\n{stops_text}")
            else:
                text_parts.append(f"\n\n🚌 Автобус {bus}:\n❌ Остановки не добавлены")
                
        except Exception as e:
            ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при получении остановок для автобуса {bus}.")
            text_parts.append(f"\n🚌 Автобус {bus}:\n⚠️ Не удалось загрузить остановки")
    
    full_text = "".join(text_parts)
    await edit_message(query.message, full_text)

@router.callback_query(F.data == "bus:get_info", admin_filter())
async def cb_get_bus_info_start(query: CallbackQuery, state: FSMContext, bus_stops_manager: BusStopsManager):
    try:
        bus_numbers = await bus_stops_manager.get_buses(get_bus_number=True)
        if not bus_numbers:
            await edit_message(query.message, "📭 В системе пока нет зарегистрированных автобусов.")
            return
    except Exception as e:
        bus_numbers = ["Ошибка при получении списка автобусов"]
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при получении списка автобусов.")
    
    await state.set_state(AdminBusInfoStates.waiting_for_bus_number)
    await edit_message(
        query.message,
        "🔍 Введите номер автобуса для получения информации:\n\n"
        "💡 Пример: 12 или 45А\n\n"
        f"**Доступные автобусы:** `{', '.join(f'`{number}`' for number in bus_numbers)}`"
    )

@router.message(AdminBusInfoStates.waiting_for_bus_number, admin_filter())
async def handle_get_bus_info(message: Message, state: FSMContext, bus_stops_manager: BusStopsManager):
    bus_number = message.text.strip()
    await state.clear()

    if not validate_bus_number(bus_number):
        await send_message(message, "❌ Неверный формат номера автобуса.")
        return

    try:
        if not await bus_stops_manager.bus_exists(bus_number=bus_number):
            await send_message(message, f"❌ Автобус с номером '{bus_number}' не найден.")
            return

        stops = await bus_stops_manager.get_stops(bus_number=bus_number, get_stop_name=True, get_stop_order=True)
        
        if not stops:
            text = f"🚌 Автобус {bus_number}\n\n❌ Остановки не добавлены."
        else:
            stops_list = [f"{stop[1]}. {stop[0]}" for stop in stops]
            text = f"🚌 Автобус {bus_number}\n\n🛑 Остановки:\n" + "\n".join(stops_list)

        await send_message(message, text)
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при получении информации об автобусе {bus_number}.")
        await send_message(message, "❌ Произошла ошибка при получении информации об автобусе.")