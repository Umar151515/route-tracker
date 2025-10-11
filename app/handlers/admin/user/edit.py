from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from core.managers import UserManager, BusStopsManager, ConfigManager
from utils.text.processing import (
    validate_phone, 
    validate_bus_number, 
    validate_name,
    normalize_identifier
)
from utils.app import send_message, edit_message
from ....keyboards.admin import (
    get_user_edit_fields_keyboard,
)
from ....states.admin import AdminUserEditStates
from ....filters import admin_filter


router = Router()

@router.callback_query(F.data == "user:edit", admin_filter())
async def cb_edit_user_ask_identifier(query: CallbackQuery, state: FSMContext):
    await state.set_state(AdminUserEditStates.waiting_for_identifier)
    await edit_message(
        query.message, 
        "✏️ **Редактирование пользователя**\n\n"
        "Введите **Telegram ID** или **номер телефона** (в формате `+996...`) пользователя, которого хотите отредактировать."
    )

@router.message(AdminUserEditStates.waiting_for_identifier, admin_filter())
async def handle_edit_identifier(message: Message, state: FSMContext, user_manager: UserManager):
    identifier = normalize_identifier(message.text)
    user_id = None
    role = None

    try:
        if validate_phone(identifier) and "+" in message.text:
            if not await user_manager.user_exists(phone_number=identifier):
                await send_message(message, "❌ Такого пользователя не существует.")
                await state.clear()
                return
            user_id, role = await user_manager.get_parameters(phone_number=identifier, get_user_id=True, get_role=True)
        
        elif identifier.isdigit():
            user_id = int(identifier)
            if not await user_manager.user_exists(user_id=user_id):
                await send_message(message, "❌ Такого пользователя не существует.")
                await state.clear()
                return
            role = await user_manager.get_parameters(user_id=user_id, get_role=True)
            
        else:
            await send_message(message, "❌ **Неверный формат!** Введите корректный ID или номер телефона.")
            await state.clear()
            return

        if user_id == message.from_user.id:
            await send_message(message, "🚫 Нельзя редактировать самого себя.")
            await state.clear()
            return

    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при поиске пользователя для редактирования: '{identifier}'.")
        await send_message(message, "❌ Произошла ошибка! Не удалось найти пользователя.")
        await state.clear()
        return

    await state.update_data(identifier=message.text)
    await state.set_state(AdminUserEditStates.waiting_for_field)
    await send_message(
        message, 
        "✅ **Пользователь найден.**\n\nТеперь выберите поле, которое хотите изменить:", 
        reply_markup=get_user_edit_fields_keyboard(role)
    )

@router.callback_query(F.data.startswith("user:edit:field:"), admin_filter())
async def cb_edit_field_choice(query: CallbackQuery, state: FSMContext, user_manager: UserManager, bus_stops_manager: BusStopsManager):
    field = query.data.split(":")[-1]

    data = await state.get_data()
    await state.update_data(field=field)
    identifier_raw = data.get("identifier")
    identifier = normalize_identifier(identifier_raw)

    try:
        if validate_phone(identifier) and "+" in identifier_raw:
            target_name = await user_manager.get_parameters(phone_number=identifier, get_name=True)
        else:
            target_name = await user_manager.get_parameters(user_id=int(identifier), get_name=True)
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при получении имени пользователя '{identifier}' перед редактированием.")
        await edit_message(query.message, "❌ Произошла ошибка! Не удалось получить данные пользователя.")
        await state.clear()
        return
    
    prompts = {
        "phone": "Введите **новый номер телефона** (в формате `+996...`).",
        "name": "Введите **новое имя**.",
        "bus_number": "Введите **новый номер автобуса**."
    }
    prompt = prompts.get(field, "Введите новое значение.")

    if field == "bus_number":
        try:
            bus_numbers = await bus_stops_manager.get_buses(get_bus_number=True)
            if not bus_numbers:
                await edit_message(query.message, "📭 В системе пока нет зарегистрированных автобусов.")
                state.clear()
                return
        except Exception as e:
            ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при получении списка автобусов для cb_edit_field_choice.")
            await edit_message(query.message, "❌ Произошла ошибка! Не удалось загрузить список доступных автобусов.")
            state.clear()
            return
        prompt += f"\n\n**Доступные автобусы:** `{', '.join(f'`{number}`' for number in bus_numbers)}`"
    
    await state.set_state(AdminUserEditStates.waiting_for_new_value)

    await edit_message(
        query.message, 
        f"✏️ **Редактирование пользователя: {target_name}**\n\n{prompt}\n\n*Для отмены отправьте `0`*"
    )

@router.message(AdminUserEditStates.waiting_for_new_value, admin_filter())
async def handle_edit_new_value(message: Message, state: FSMContext, user_manager: UserManager, bus_stops_manager: BusStopsManager):
    data = await state.get_data()
    identifier_raw = data.get("identifier")
    identifier = normalize_identifier(identifier_raw)
    field = data.get("field")
    new_value = message.text.strip()
    
    await state.clear()

    if new_value == "0":
        await send_message(message, "↩️ Редактирование отменено.")
        return
    if not identifier or not field:
        await send_message(message, "❌ Критическая ошибка! Данные для редактирования потеряны. Начните заново.")
        return

    try:
        kwargs_search = {}
        if validate_phone(identifier) and "+" in identifier_raw:
            kwargs_search["phone_number"] = identifier
        else:
            kwargs_search["user_id"] = int(identifier)

        kwargs_update = {}
        if field == "phone" and validate_phone(normalize_identifier(new_value)):
            kwargs_update["new_phone_number"] = normalize_identifier(new_value)
        elif field == "name" and validate_name(new_value):
            kwargs_update["new_name"] = new_value
        elif field == "bus_number" and validate_bus_number(new_value):
            try:
                bus_numbers = await bus_stops_manager.get_buses(get_bus_number=True)
                if new_value in bus_numbers:
                    kwargs_update["new_bus_number"] = new_value
                else:
                    await send_message(message, f"❌ Такого автобуса не существует.")
                    return
            except Exception as e:
                ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при получении списка автобусов для cb_edit_field_choice.")
                await send_message(message, "❌ Произошла ошибка! Не удалось загрузить список доступных автобусов.")
                return
        else:
            await send_message(message, f"❌ **Неверный формат!** Введенное значение «{new_value}» некорректно. Попробуйте снова.")
            return

        await user_manager.set_user(**kwargs_search, **kwargs_update)
        await send_message(message, "✅ **Успешно!** Данные пользователя обновлены.")

    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при обновлении поля '{field}' для пользователя '{identifier}'.")
        await send_message(message, "❌ Произошла ошибка! Не удалось обновить данные пользователя. Возможно, такой номер телефона уже занят.")