from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from core.managers import GoogleSheetsManager, ConfigManager
from utils.app import send_message, edit_message
from ....states.admin import AdminSheetsStates
from ....filters import admin_filter


router = Router()

@router.callback_query(F.data == "sheets:get_data", admin_filter())
async def cb_get_data_start(query: CallbackQuery, state: FSMContext):
    await state.set_state(AdminSheetsStates.waiting_for_days_to_get)
    await edit_message(
        query.message,
        "📊 Получение данных из таблицы\n\n"
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
            days_text = "все данные"
        else:
            days = int(days_str)
            if days <= 0:
                await send_message(message, "❌ Количество дней должно быть положительным числом.")
                return
            days_text = f"{days} последних дней"
    except ValueError:
        await send_message(message, "❌ Неверный формат числа. Введите целое число.")
        return

    try:
        data = await sheets_manager.get_last_n_days_data(days)

    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при получении данных таблицы.")
        await send_message(message, "❌ Произошла ошибка при получении данных из таблицы.")
        return

    if not data:
        text = "Нет данных."
    else:
        header = data[0]
        records = data[1:]
        
        text = (
            f"📊 <b>Данные из таблицы ({days_text})</b>\n"
            f"📈 Всего записей: <b>{len(records)}</b>\n\n"
        )

        header_text = " | ".join(f"<b>{h}</b>" for h in header)
        text += f"🧾 <b>Заголовки:</b>\n{header_text}\n\n"

        for i, record in enumerate(records, 1):
            row_text = "\n".join(
                [f"<b>{header[j]}:</b> {record[j]}" for j in range(len(header))]
            )
            text += f"🔹 <b>Запись {i}</b>\n{row_text}\n\n"

    await send_message(message, text, parse_mode=ParseMode.HTML)
