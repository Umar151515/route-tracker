from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from core.managers import UserManager, BusStopsManager, ConfigManager
from utils.text.processing import (
    validate_phone, 
    validate_bus_number, 
    parse_comma_list, 
    format_user_record, 
    normalize_identifier
)
from ....utils import send_message, edit_message
from ....keyboards.admin import (
    user_settings_keyboard,
    user_filters_keyboard,
    user_roles_filter_keyboard,
)
from ....states.admin import AdminUserStates
from ....filters import admin_filter


router = Router()

@router.message(F.text == "👥 Настройки пользователей", admin_filter())
async def user_settings(message: Message):
    await send_message(
        message, 
        "⚙️ **Настройки пользователей**\n\nВыберите, что хотите сделать:", 
        reply_markup=user_settings_keyboard
    )

@router.callback_query(F.data == "user:get_all", admin_filter())
async def cb_get_all_menu(query: CallbackQuery):
    await edit_message(
        query.message, 
        "👥 **Получение списка пользователей**\n\nВыберите, по какому критерию отфильтровать список:", 
        reply_markup=user_filters_keyboard
    )

@router.callback_query(F.data == "user:get_all:all", admin_filter())
async def cb_get_all_all(query: CallbackQuery, user_manager: UserManager):
    try:
        users = await user_manager.get_users()
        if not users:
            await edit_message(query.message, "🤷‍♂️ В базе данных пока нет ни одного пользователя.")
            return

        user_lines = [
            format_user_record(u["name"], u["role"], u["phone_number"], u["user_id"], u["bus_number"]) 
            for u in users
        ]
        users_text = "\n".join(user_lines)
        text = f"✅ **Найдено пользователей: {len(users)}**\n\n{users_text}"

        await edit_message(query.message, text)

    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при получении списка ВСЕХ пользователей.")
        await edit_message(query.message, "❌ Произошла ошибка! Не удалось получить список пользователей. Попробуйте позже.")

@router.callback_query(F.data == "user:get_all:by_role_menu", admin_filter())
async def cb_get_all_by_role_menu(query: CallbackQuery):
    await edit_message(
        query.message,
        "🎭 **Фильтр по ролям**\n\nВыберите роль, чтобы увидеть список пользователей:",
        reply_markup=user_roles_filter_keyboard
    )

@router.callback_query(F.data.startswith("user:get_all:by_role:"), admin_filter())
async def cb_get_all_by_role_selected(query: CallbackQuery, user_manager: UserManager):
    role = query.data.split(":")[-1]
    
    role_name_ru = "Водители" if role == "driver" else "Администраторы"

    try:
        users = await user_manager.get_users(roles=[role])
        if not users:
            await edit_message(query.message, f"🤷‍♂️ Пользователи с ролью «{role_name_ru}» не найдены.")
            return

        user_lines = [
            format_user_record(u["name"], u["role"], u["phone_number"], u["user_id"], u["bus_number"]) 
            for u in users
        ]
        users_text = "\n".join(user_lines)
        text = f"👥 **{role_name_ru} ({len(users)} чел.)**\n\n{users_text}"
        
        await edit_message(query.message, text)

    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при получении пользователей по роли '{role}'.")
        await edit_message(query.message, f"❌ Произошла ошибка! Не удалось получить список для роли «{role_name_ru}».")

@router.callback_query(F.data == "user:get_all:by_bus", admin_filter())
async def cb_get_all_by_bus_start(query: CallbackQuery, state: FSMContext, bus_stops_manager: BusStopsManager):
    try:
        bus_numbers = await bus_stops_manager.get_buses(get_bus_number=True)
        if not bus_numbers:
            await edit_message(query.message, "📭 В системе пока нет зарегистрированных автобусов.")
            await state.clear()
            return
            
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при получении списка автобусов для фильтра.")
        await edit_message(query.message, "❌ Произошла ошибка! Не удалось загрузить список доступных автобусов.")
        await state.clear()
        return

    await state.set_state(AdminUserStates.waiting_for_bus_filter)
    await edit_message(
        query.message,
        "🚌 **Фильтр по автобусу**\n\n"
        "Введите один или несколько номеров автобусов через запятую (например: `12`, `45А`).\n\n"
        f"**Доступные автобусы:** `{', '.join(f'`{number}`' for number in bus_numbers)}`"
    )

@router.message(AdminUserStates.waiting_for_bus_filter, admin_filter())
async def handle_bus_filter_input(message: Message, state: FSMContext, user_manager: UserManager):
    await state.clear()
    bus_numbers = parse_comma_list(message.text)

    for bus_number in bus_numbers:
        if not validate_bus_number(bus_number):
            await send_message(message, f"❌ **Неверный формат!** Номер «{bus_number}» некорректен. Попробуйте снова.")
            return

    try:
        users = await user_manager.get_users(bus_numbers=bus_numbers)
        if not users:
            await send_message(message, "🤷‍♂️ Водители для указанных автобусов не найдены.")
            return
        
        user_lines = [
            format_user_record(u["name"], u["role"], u["phone_number"], u["user_id"], u["bus_number"]) 
            for u in users
        ]
        users_text = "\n".join(user_lines)
        text = f"✅ **Найдено водителей: {len(users)}**\n\n{users_text}"
        
        await send_message(message, text)

    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при поиске пользователей по номерам автобусов: {bus_numbers}.")
        await send_message(message, "❌ Произошла ошибка! Не удалось выполнить поиск. Попробуйте позже.")

@router.callback_query(F.data == "user:get_info", admin_filter())
async def cb_get_user_info_start(query: CallbackQuery, state: FSMContext):
    await state.set_state(AdminUserStates.waiting_for_identifier)
    await edit_message(
        query.message, 
        "🔍 **Поиск пользователя**\n\n"
        "Введите **Telegram ID** или **номер телефона** (в формате `+996...`) пользователя, чтобы получить информацию о нём."
    )

@router.message(AdminUserStates.waiting_for_identifier, admin_filter())
async def handle_get_user_info(message: Message, state: FSMContext, user_manager: UserManager):
    await state.clear()
    identifier = normalize_identifier(message.text)
    
    params = {
        'get_phone_number': True, 'get_user_id': True, 'get_role': True,
        'get_name': True, 'get_bus_number': True
    }
    
    try:
        if validate_phone(identifier) and "+" in message.text:
            result = await user_manager.get_parameters(phone_number=identifier, **params)
        elif identifier.isdigit():
            result = await user_manager.get_parameters(user_id=int(identifier), **params)
        else:
            await send_message(message, "❌ **Неверный формат!** Введите корректный ID или номер телефона.")
            return

        if result is None:
            await send_message(message, "🤷‍♂️ Пользователь с такими данными не найден.")
            return

        phone_number, user_id, role, name, bus_number = result

        await send_message(
            message, 
            f"**ℹ️ Информация о пользователе:**\n\n"
            f"{format_user_record(name, role, phone_number, user_id, bus_number)}"
        )

    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при получении информации о пользователе по идентификатору '{identifier}'.")
        await send_message(message, "❌ Произошла ошибка! Не удалось получить информацию о пользователе.")