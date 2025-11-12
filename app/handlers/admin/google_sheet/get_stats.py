from datetime import date

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

from core.managers import GoogleSheetsManager, ConfigManager
from core.managers.bus_stops_manager import BusStopsManager
from utils.app import send_message, edit_message, delete_message
from utils.text.processing import validate_date
from ....states.admin import AdminSheetsStates
from ....filters import admin_filter
from ....keyboards.admin import (
    sheets_stats_date_filter_keyboard,
    sheets_stats_bus_filter_keyboard
)


router = Router()

@router.callback_query(F.data == "sheets:get_stats", admin_filter())
async def cb_get_stats_start(query: CallbackQuery, state: FSMContext):
    await state.set_state(AdminSheetsStates.waiting_for_stats_date_filter_type)
    await edit_message(
        query.message,
        "📈 **Получение статистики из таблицы**\n\n"
        "Выберите тип фильтрации по датам:",
        reply_markup=sheets_stats_date_filter_keyboard
    )

@router.callback_query(F.data.startswith("sheets:stats_date_filter:"), AdminSheetsStates.waiting_for_stats_date_filter_type, admin_filter())
async def cb_stats_date_filter_type(query: CallbackQuery, state: FSMContext):
    filter_type = query.data.split(":")[-1]
    
    await state.update_data(date_filter_type=filter_type)
    
    if filter_type == "specific":
        await state.set_state(AdminSheetsStates.waiting_for_stats_specific_date)
        await edit_message(
            query.message,
            "📅 **Фильтр по конкретной дате**\n\n"
            "Введите дату в формате `ГГГГ-ММ-ДД`:\n\n"
            f"💡 Пример: `{date.today().strftime('%Y-%m-%d')}`\n"
            "*Для отмены отправьте 0*"
        )
    elif filter_type == "first_days":
        await state.set_state(AdminSheetsStates.waiting_for_stats_days_count)
        await edit_message(
            query.message,
            "🔢 **Фильтр по первым N дням**\n\n"
            "Введите количество первых дней для выборки:\n\n"
            "💡 Пример: 7 (покажет данные за первые 7 дней)\n"
            "*Для отмены отправьте 0*"
        )
    elif filter_type == "last_days":
        await state.set_state(AdminSheetsStates.waiting_for_stats_days_count)
        await edit_message(
            query.message,
            "🔢 **Фильтр по последним N дням**\n\n"
            "Введите количество последних дней для выборки:\n\n"
            "💡 Пример: 7 (покажет данные за последние 7 дней)\n"
            "*Для отмены отправьте 0*"
        )
    elif filter_type == "date_range":
        await state.set_state(AdminSheetsStates.waiting_for_stats_start_date)
        await edit_message(
            query.message,
            "📅 **Фильтр по диапазону дат**\n\n"
            "Введите **начальную** дату в формате `ГГГГ-ММ-ДД`:\n\n"
            f"💡 Пример: `{date.today().strftime('%Y-%m-%d')}`\n"
            "*Для отмены отправьте 0*"
        )
    elif filter_type == "all":
        await delete_message(query.message)
        await ask_stats_bus_filter(query.message, state)

@router.message(AdminSheetsStates.waiting_for_stats_specific_date, admin_filter())
async def handle_stats_specific_date(message: Message, state: FSMContext):
    date_str = message.text.strip().replace(" ", "-")
    
    if date_str == "0":
        await state.clear()
        await send_message(message, "↩️ Получение статистики отменено.")
        return
    
    if not validate_date(date_str):
        await send_message(message, "❌ **Неверный формат даты!** Введите дату в формате `ГГГГ-ММ-ДД`.")
        return
    
    await state.update_data(specific_date=date_str)
    await ask_stats_bus_filter(message, state)

@router.message(AdminSheetsStates.waiting_for_stats_days_count, admin_filter())
async def handle_stats_days_count(message: Message, state: FSMContext):
    days_str = message.text.strip()
    
    if days_str == "0":
        await state.clear()
        await send_message(message, "↩️ Получение статистики отменено.")
        return
    
    try:
        days = int(days_str)
        if days <= 0:
            await send_message(message, "❌ **Количество дней должно быть положительным числом!**")
            return
    except ValueError:
        await send_message(message, "❌ **Неверный формат числа!** Введите целое число.")
        return
    
    data = await state.get_data()
    filter_type = data.get("date_filter_type")
    
    if filter_type == "first_days":
        await state.update_data(first_days_count=days)
    elif filter_type == "last_days":
        await state.update_data(last_days_count=days)
    
    await ask_stats_bus_filter(message, state)

@router.message(AdminSheetsStates.waiting_for_stats_start_date, admin_filter())
async def handle_stats_start_date(message: Message, state: FSMContext):
    start_date = message.text.strip().replace(" ", "-")
    
    if start_date == "0":
        await state.clear()
        await send_message(message, "↩️ Получение статистики отменено.")
        return
    
    if not validate_date(start_date):
        await send_message(message, "❌ **Неверный формат даты!** Введите дату в формате `ГГГГ-ММ-ДД`.")
        return
    
    await state.update_data(start_date=start_date)
    await state.set_state(AdminSheetsStates.waiting_for_stats_end_date)
    
    await send_message(
        message,
        "📅 **Фильтр по диапазону дат**\n\n"
        "Введите **конечную** дату в формате `ГГГГ-ММ-ДД`:\n\n"
        f"💡 Пример: `{date.today().strftime('%Y-%m-%d')}`\n"
        "*Для отмены отправьте 0*"
    )

@router.message(AdminSheetsStates.waiting_for_stats_end_date, admin_filter())
async def handle_stats_end_date(message: Message, state: FSMContext):
    end_date = message.text.strip().replace(" ", "-")
    
    if end_date == "0":
        await state.clear()
        await send_message(message, "↩️ Получение статистики отменено.")
        return
    
    if not validate_date(end_date):
        await send_message(message, "❌ **Неверный формат даты!** Введите дату в формате `ГГГГ-ММ-ДД`.")
        return
    
    await state.update_data(end_date=end_date)
    await ask_stats_bus_filter(message, state)

async def ask_stats_bus_filter(message: Message, state: FSMContext):
    await state.set_state(AdminSheetsStates.waiting_for_stats_bus_filter)
    await send_message(
        message,
        "🚌 **Фильтрация по автобусам**\n\n"
        "Выберите как фильтровать данные:",
        reply_markup=sheets_stats_bus_filter_keyboard
    )

@router.callback_query(F.data.startswith("sheets:stats_bus_filter:"), AdminSheetsStates.waiting_for_stats_bus_filter, admin_filter())
async def cb_stats_bus_filter(
    query: CallbackQuery,
    state: FSMContext,
    sheets_manager: GoogleSheetsManager,
    bus_stops_manager: BusStopsManager
):
    bus_filter = query.data.split(":")[-1]
    try:
        bus_numbers = await bus_stops_manager.get_buses(get_bus_number=True)
        if not bus_numbers:
            await edit_message(query.message, "📭 В системе пока нет зарегистрированных автобусов.")
            return
    except Exception as e:
        bus_numbers = ["Ошибка при получении списка автобусов"]
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при получении списка автобусов.")
    
    if bus_filter == "specific":
        await state.set_state(AdminSheetsStates.waiting_for_stats_bus_numbers)
        await edit_message(
            query.message,
            "🚌 **Фильтр по конкретным автобусам**\n\n"
            "Введите номера автобусов через запятую:\n\n"
            "*Для отмены отправьте 0*\n\n"
            f"**Зарегистрированные автобусы в БД:** `{', '.join(f'`{number}`' for number in bus_numbers)}`"
        )
    else:
        await delete_message(query.message)
        await state.update_data(bus_filter=bus_filter)
        await show_stats_data(query.message, state, sheets_manager)

@router.message(AdminSheetsStates.waiting_for_stats_bus_numbers, admin_filter())
async def handle_stats_bus_numbers(message: Message, state: FSMContext, sheets_manager: GoogleSheetsManager):
    bus_numbers_str = message.text.strip()
    
    if bus_numbers_str == "0":
        await state.clear()
        await send_message(message, "↩️ Получение статистики отменено.")
        return
    
    bus_numbers = [bus.strip() for bus in bus_numbers_str.split(",") if bus.strip()]
    if not bus_numbers:
        await send_message(message, "❌ **Неверный формат!** Введите номера через запятую.")
        return
    
    await state.update_data(bus_filter="specific", bus_numbers=bus_numbers)
    await show_stats_data(message, state, sheets_manager)

async def show_stats_data(message: Message, state: FSMContext, sheets_manager: GoogleSheetsManager):
    data = await state.get_data()
    await state.clear()
    
    try:
        filter_params = {}
        
        date_filter_type = data.get("date_filter_type")
        if date_filter_type == "specific":
            filter_params["date_str"] = data.get("specific_date")
        elif date_filter_type == "first_days":
            filter_params["first_days_count"] = data.get("first_days_count")
        elif date_filter_type == "last_days":
            filter_params["last_days_count"] = data.get("last_days_count")
        elif date_filter_type == "date_range":
            filter_params["start_date_str"] = data.get("start_date")
            filter_params["end_date_str"] = data.get("end_date")
        
        bus_filter = data.get("bus_filter")
        if bus_filter == "specific":
            filter_params["bus_numbers"] = data.get("bus_numbers")
        
        sheets_data = await sheets_manager.get_filters_data(**filter_params)
        
        if not sheets_data or len(sheets_data) <= 1:
            await send_message(message, "📭 **Нет данных**, соответствующих выбранным фильтрам.")
            return
        
        records = sheets_data[1:]
        
        stats_by_date = {}
        
        for record in records:
            if len(record) < 6:
                continue
                
            date_val = record[0]
            bus_number = record[3] if len(record) > 3 else "Неизвестно"
            passengers_str = record[5] if len(record) > 5 else "0"
            
            if not passengers_str.isdigit():
                continue
                
            passengers = int(passengers_str)
            
            if date_val not in stats_by_date:
                stats_by_date[date_val] = {}
            
            if bus_number not in stats_by_date[date_val]:
                stats_by_date[date_val][bus_number] = 0
                
            stats_by_date[date_val][bus_number] += passengers
        
        filters_text = _build_stats_filters_text(data)
        total_passengers_all = 0
        
        text = (
            f"📈 Статистика по пассажирам\n\n"
            f"Примененные фильтры:\n{filters_text}\n\n"
        )
        
        for date_val in sorted(stats_by_date.keys()):
            date_stats = stats_by_date[date_val]
            total_passengers_date = sum(date_stats.values())
            total_passengers_all += total_passengers_date
            
            text += f"📅 Дата: {date_val}\n"
            text += f"🚌 По автобусам:\n"
            
            for bus_number in sorted(date_stats.keys()):
                passengers = date_stats[bus_number]
                text += f"   • {bus_number}: {passengers} пассажиров\n"
            
            text += f"Всего за день: {total_passengers_date} пассажиров\n\n"
        
        text += f"Общее количество пассажиров за период: {total_passengers_all}"

        if len(text) > 4000:
            file_data = text.encode('utf-8')
            
            file = BufferedInputFile(file_data, filename="table_data.txt")
            
            await message.answer_document(
                file,
                caption=f"📁 Данные таблицы ({len(records)} записей)."
            )
        else:
            await send_message(message, text)
        
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при получении статистики с фильтрами")
        await send_message(message, "❌ **Произошла ошибка!** Не удалось получить статистику.")

def _build_stats_filters_text(data: dict) -> str:
    filters = []
    
    date_filter_type = data.get("date_filter_type")
    if date_filter_type == "specific":
        filters.append(f"• Дата: {data.get('specific_date')}")
    elif date_filter_type == "first_days":
        filters.append(f"• Первые {data.get('first_days_count')} дней")
    elif date_filter_type == "last_days":
        filters.append(f"• Последние {data.get('last_days_count')} дней")
    elif date_filter_type == "date_range":
        filters.append(f"• Диапазон: {data.get('start_date')} - {data.get('end_date')}")
    elif date_filter_type == "all":
        filters.append("• Все даты")
    
    bus_filter = data.get("bus_filter")
    if bus_filter == "specific":
        filters.append(f"• Автобусы: {', '.join(data.get('bus_numbers', []))}")
    elif bus_filter == "all":
        filters.append("• Все автобусы")
    
    return "\n".join(filters) if filters else "• Без фильтров"