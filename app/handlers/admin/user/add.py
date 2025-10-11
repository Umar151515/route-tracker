from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from core.managers import UserManager, BusStopsManager, ConfigManager
from utils.text.processing import (
    validate_phone, 
    validate_bus_number, 
    validate_name,
    normalize_identifier,
    translate_role
)
from ....utils import send_message, edit_message, delete_message
from ....keyboards.admin import user_add_role_keyboard
from ....states.admin import AdminUserAddStates
from ....filters import admin_filter


router = Router()

@router.callback_query(F.data == "user:add", admin_filter())
async def cb_add_user_start(query: CallbackQuery, state: FSMContext):
    await state.set_state(AdminUserAddStates.waiting_for_phone)
    await edit_message(
        query.message,
        "➕ **Добавление нового пользователя**\n\n"
        "Введите **номер телефона** нового пользователя (в формате `+996...`):\n\n"
        "*Для отмены отправьте 0*"
    )

@router.message(AdminUserAddStates.waiting_for_phone, admin_filter())
async def handle_add_user_phone(message: Message, state: FSMContext, user_manager: UserManager):
    phone = normalize_identifier(message.text.strip())
    
    if message.text.strip() == "0":
        await state.clear()
        await send_message(message, "↩️ Добавление пользователя отменено.")
        return
    
    if not validate_phone(phone) or "+" not in message.text:
        await send_message(message, "❌ **Неверный формат!** Введите корректный номер телефона в формате `+996...`.")
        return
    
    try:
        if await user_manager.user_exists(phone_number=phone):
            await send_message(message, "❌ **Пользователь с таким номером телефона уже существует! Попробуйте ещё раз.**")
            return
            
        await state.update_data(phone=phone)
        await state.set_state(AdminUserAddStates.waiting_for_name)
        await send_message(
            message,
            "✅ **Номер телефона принят.**\n\n"
            "Введите **имя** нового пользователя:\n\n"
            "*Для отмены отправьте 0*"
        )
        
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при проверке телефона для добавления пользователя: '{phone}'")
        await send_message(message, "❌ Произошла ошибка! Не удалось проверить номер телефона.")

@router.message(AdminUserAddStates.waiting_for_name, admin_filter())
async def handle_add_user_name(message: Message, state: FSMContext):
    name = message.text.strip()
    
    if name == "0":
        await state.clear()
        await send_message(message, "↩️ Добавление пользователя отменено.")
        return
    
    if not validate_name(name):
        await send_message(message, "❌ Неверный формат имени!")
        return
    
    await state.update_data(name=name)
    await state.set_state(AdminUserAddStates.waiting_for_role)
    await send_message(
        message,
        "✅ **Имя принято.**\n\n"
        "Выберите **роль** пользователя:",
        reply_markup=user_add_role_keyboard
    )

@router.callback_query(F.data.startswith("user:add:role:"), admin_filter())
async def cb_add_user_role(query: CallbackQuery, state: FSMContext, bus_stops_manager: BusStopsManager):
    role = query.data.split(":")[-1]
    data = await state.get_data()
    
    await state.update_data(role=role)
    
    if role == "driver":
        try:
            bus_numbers = await bus_stops_manager.get_buses(get_bus_number=True)
            if not bus_numbers:
                await edit_message(query.message, "📭 В системе пока нет зарегистрированных автобусов. Невозможно добавить водителя.")
                await state.clear()
                return
                
            await state.set_state(AdminUserAddStates.waiting_for_bus_number)
            await edit_message(
                query.message,
                f"🎯 **Роль: Водитель**\n\n"
                f"Введите **номер автобуса** для водителя:\n\n"
                f"**Доступные автобусы:** `{', '.join(f'`{number}`' for number in bus_numbers)}`\n\n"
                f"*Для отмены отправьте 0*"
            )
        except Exception as e:
            ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при получении списка автобусов для добавления водителя")
            await edit_message(query.message, "❌ Произошла ошибка! Не удалось загрузить список автобусов.")
            await state.clear()
    else:
        await finish_user_creation(query.message, state, bus_number="")

async def finish_user_creation(message: Message, state: FSMContext, bus_number: str | None = None):
    data = await state.get_data()
    phone = data.get("phone")
    name = data.get("name")
    role = data.get("role")
    user_manager = await UserManager.create()
    
    try:
        await user_manager.create_user(
            phone_number=phone,
            role=role,
            name=name,
            bus_number=bus_number
        )
        
        bus_info = f"**Автобус:** {bus_number}" if role == "driver" else ""
        if role == "admin":
            await delete_message(message)
        
        ConfigManager.log.logger.info(f"Администратор ID - {message.from_user.id} добавил пользователя {name}")

        await send_message(
            message,
            f"✅ **Пользователь успешно добавлен!**\n\n"
            f"**Имя:** {name}\n"
            f"**Телефон:** `+{phone}`\n"
            f"**Роль:** {translate_role(role)}\n"
            f"{bus_info}"
        )
        await state.clear()
        
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при создании пользователя: {phone}, {name}, {role}, {bus_number}")
        await send_message(message, "❌ Произошла ошибка! Не удалось создать пользователя.")
        await state.clear()

@router.message(AdminUserAddStates.waiting_for_bus_number, admin_filter())
async def handle_add_user_bus_number(message: Message, state: FSMContext, bus_stops_manager: BusStopsManager):
    bus_number = message.text.strip()
    
    if bus_number == "0":
        await state.clear()
        await send_message(message, "↩️ Добавление пользователя отменено.")
        return
    
    if not validate_bus_number(bus_number):
        await send_message(message, "❌ **Неверный формат номера автобуса!**")
        return
    
    try:
        bus_numbers = await bus_stops_manager.get_buses(get_bus_number=True)
        if bus_number not in bus_numbers:
            await send_message(message, f"❌ **Автобус с номером '{bus_number}' не существует!** Попробуйте ещё раз.")
            return
            
        await finish_user_creation(message, state, bus_number)
        
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при проверке автобуса для добавления пользователя: '{bus_number}'")
        await send_message(message, "❌ Произошла ошибка! Не удалось проверить номер автобуса.")
