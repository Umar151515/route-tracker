from datetime import date
import io

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

from core.managers import GoogleSheetsManager, ConfigManager
from utils.app import send_message, edit_message
from ....states.admin import AdminSheetsStates
from ....filters import admin_filter
from ....keyboards.admin import sheets_settings_keyboard


router = Router()

@router.message(F.text == "📄 Настройки гугл таблицы", admin_filter())
async def sheets_settings(message: Message):
    await send_message(message, "📄 Панель управления данными таблиц", reply_markup=sheets_settings_keyboard)

@router.callback_query(F.data == "sheets:get_data", admin_filter())
async def cb_get_data_start(query: CallbackQuery, state: FSMContext):
    """Получение сырых данных за последние N дней"""
    await state.set_state(AdminSheetsStates.waiting_for_days_to_get)
    await edit_message(
        query.message,
        "📊 **Получение данных из таблицы**\n\n"
        "🔢 Введите количество последних дней для выгрузки:\n\n"
        "💡 Пример: 7 (покажет данные за последние 7 дней)\n"
        "💡 Введите 0 для получения всех данных"
    )

@router.message(AdminSheetsStates.waiting_for_days_to_get, admin_filter())
async def handle_get_data(
    message: Message,
    state: FSMContext,
    sheets_manager: GoogleSheetsManager
):
    days_str = message.text.strip()
    await state.clear()

    try:
        if not days_str or days_str == "0":
            days = None
        else:
            days = int(days_str)
            if days <= 0:
                await send_message(message, "❌ Количество дней должно быть положительным числом.")
                return
    except ValueError:
        await send_message(message, "❌ Неверный формат числа. Введите целое число.")
        return

    try:
        data = await sheets_manager.get_filters_data(last_days_count=days)

    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при получении данных таблицы.")
        await send_message(message, "❌ Произошла ошибка при получении данных из таблицы.")
        return

    if not data:
        await send_message(message, "📭 **Нет данных**")
        return

    header = data[0]
    records = data[1:]
    
    stats = {}
    total_passengers = 0
    
    for record in records:
        if len(record) > 5 and record[5].isdigit():
            passengers = int(record[5])
            total_passengers += passengers
            
            driver_name = record[2] if len(record) > 2 else "Неизвестно"
            bus_number = record[3] if len(record) > 3 else "Неизвестно"
            if (driver_name, bus_number) in stats:
                stats[(driver_name, bus_number)] += passengers
            else:
                stats[(driver_name, bus_number)] = passengers

    stats_text = (
        f"📊 Данные из таблицы\n"
        f"📈 Всего записей: {len(records)}\n\n"
        f"👥 Статистика:\n"
    )
    
    for name, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        stats_text += f"• Водитель - {name[0]}, автобус - {name[1]}: {count} пассажиров\n"
    
    stats_text += f"\nОбщее количество пассажиров: {total_passengers}"

    await send_message(message, stats_text)

    detailed_text = ""

    for i, record in enumerate(records, 1):
        row_text = "\n".join(
            [f"{header[j]}: {record[j]}" for j in range(len(header))]
        )
        detailed_text += f"Запись {i}:\n{row_text}\n\n"

    if len(detailed_text) > 4000:
        file_data = detailed_text.encode('utf-8')
        
        file = BufferedInputFile(file_data, filename="table_data.txt")
        
        await message.answer_document(
            file,
            caption=f"📁 Данные таблицы ({len(records)} записей)."
        )
    else:
        await send_message(message, detailed_text)