from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from core.managers import GoogleSheetsManager, ConfigManager
from utils.app import send_message, edit_message
from ....keyboards.admin import sheets_settings_keyboard, confirm_delete_keyboard
from ....states.admin import AdminSheetsStates
from ....filters import admin_filter


router = Router()

@router.message(F.text == "📄 Настройки гугл таблицы", admin_filter())
async def sheets_settings(message: Message):
    await send_message(message, "📄 Панель управления данными таблиц", reply_markup=sheets_settings_keyboard)

@router.callback_query(F.data == "sheets:delete_data", admin_filter())
async def cb_delete_data_start(query: CallbackQuery, state: FSMContext):
    await state.set_state(AdminSheetsStates.waiting_for_days_to_delete)
    await edit_message(
        query.message,
        "🗑 Удаление данных из таблицы\n\n"
        "🔢 Введите количество дней для удаления (с начала таблицы):\n\n"
        "💡 Пример: 7 (удалит данные за первые 7 дней)\n"
        "⚠️ Внимание: Это действие нельзя отменить!"
    )

@router.message(AdminSheetsStates.waiting_for_days_to_delete, admin_filter())
async def handle_delete_data(
    message: Message,
    state: FSMContext,
    sheets_manager: GoogleSheetsManager
):
    days_str = message.text.strip()

    if days_str.isdigit():
        days = int(days_str)
        if days <= 0:
            await send_message(message, "❌ Количество дней должно быть положительным числом.")
            await state.clear()
            return
    else:
        await send_message(message, "❌ Неверный формат числа. Введите целое число.")
        await state.clear()
        return
    try:
        current_data = await sheets_manager.get_last_n_days_data()
        if not current_data or len(current_data) <= 1:
            await send_message(message, "❌ В таблице нет данных для удаления.")
            await state.clear()
            return
        
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при проверке данных таблицы")
        await send_message(message, "❌ Произошла ошибка при проверке данных таблицы.")
        await state.clear()

    unique_dates = set()
    for row in current_data[1:]:
        if len(row) > 0 and row[0]:
            unique_dates.add(row[0])
    
    total_days = len(unique_dates)
    
    if days > total_days:
        await send_message(
            message, 
            f"❌ В таблице всего {total_days} дней данных. Нельзя удалить {days} дней."
        )
        await state.clear()
        return

    await state.update_data(
        days_to_delete=days, 
        total_days=total_days,
        records_count=len(current_data) - 1,
        admin_id=message.from_user.id
    )
    
    await state.set_state(AdminSheetsStates.confirm_delete)
    
    await send_message(
        message,
        f"⚠️ Подтверждение удаления\n\n"
        f"📅 Будет удалено данных за первые {days} дней\n"
        f"📊 Всего дней в таблице: {total_days}\n"
        f"📝 Записей будет удалено: {len(current_data) - 1}\n\n"
        f"❌ Это действие нельзя отменить!",
        reply_markup=confirm_delete_keyboard
    )

@router.callback_query(F.data == "sheets:confirm_delete:yes", AdminSheetsStates.confirm_delete, admin_filter())
async def handle_confirm_delete_yes(
    query: CallbackQuery,
    state: FSMContext,
    sheets_manager: GoogleSheetsManager
):
    data = await state.get_data()
    days = data.get('days_to_delete')
    admin_id = data.get('admin_id')
    records_count = data.get('records_count')
    
    await state.clear()

    try:
        ConfigManager.log.logger.info(
            f"🛑 Администратор ID: {admin_id} инициировал удаление данных таблицы. "
            f"Удаляется {days} дней, записей: {records_count}"
        )
        
        await sheets_manager.clear_first_n_days(days)
        
        await edit_message(
            query.message,
            f"✅ Данные успешно удалены!\n\n"
            f"🗑 Удалено данных за {days} дней\n"
            f"📝 Количество записей: {records_count}\n"
            f"📅 Таблица очищена от старых записей"
        )
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при удалении данных администратором ID: {admin_id}")
        await edit_message(query.message, f"❌ Произошла ошибка при удалении данных из таблицы.\n")