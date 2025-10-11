from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from core.managers import UserManager, ConfigManager
from utils.text.processing import translate_role
from utils.text.processing import validate_phone, normalize_identifier
from ....utils import send_message, edit_message
from ....keyboards.admin import user_delete_confirm_keyboard
from ....states.admin import AdminUserDeleteStates
from ....filters import admin_filter


router = Router()

@router.callback_query(F.data == "user:delete", admin_filter())
async def cb_delete_user_start(query: CallbackQuery, state: FSMContext):
    await state.set_state(AdminUserDeleteStates.waiting_for_identifier)
    await edit_message(
        query.message,
        "🗑️ **Удаление пользователя**\n\n"
        "Введите **Telegram ID** или **номер телефона** (в формате `+996...`) пользователя, которого хотите удалить:\n\n"
        "*Для отмены отправьте `0`*"
    )

@router.message(AdminUserDeleteStates.waiting_for_identifier, admin_filter())
async def handle_delete_user_identifier(message: Message, state: FSMContext, user_manager: UserManager):
    identifier = normalize_identifier(message.text.strip())
    
    if message.text.strip() == "0":
        await state.clear()
        await send_message(message, "↩️ Удаление пользователя отменено.")
        return
    
    try:
        user_exists = False
        user_info = None
        
        if validate_phone(identifier) and "+" in message.text:
            user_exists = await user_manager.user_exists(phone_number=identifier)
            if user_exists:
                user_info = await user_manager.get_parameters(
                    phone_number=identifier, 
                    get_user_id=True, get_name=True, get_role=True, get_bus_number=True
                )
        elif identifier.isdigit():
            user_exists = await user_manager.user_exists(user_id=int(identifier))
            if user_exists:
                user_info = await user_manager.get_parameters(
                    user_id=int(identifier),
                    get_phone_number=True, get_name=True, get_role=True, get_bus_number=True
                )
        else:
            await send_message(message, "❌ **Неверный формат!** Введите корректный ID или номер телефона.")
            return
        
        if not user_exists or not user_info:
            await send_message(message, "❌ **Пользователь не найден!**")
            await state.clear()
            return
        
        if validate_phone(identifier) and "+" in message.text:
            user_id, role, name, bus_number = user_info
            phone_number = identifier
        else:
            phone_number, role, name, bus_number = user_info
            user_id = int(identifier)
        
        if user_id == message.from_user.id:
            await send_message(message, "🚫 **Нельзя удалить самого себя!**")
            await state.clear()
            return
        
        await state.update_data(
            identifier=message.text,
            user_id=user_id,
            phone_number=phone_number,
            name=name,
            role=role,
            bus_number=bus_number
        )
        
        bus_info = f"\n**Автобус:** {bus_number}" if role == "driver" else ""
        
        await send_message(
            message,
            f"⚠️ **Подтверждение удаления**\n\n"
            f"**Вы действительно хотите удалить пользователя?**\n\n"
            f"**Имя:** {name}\n"
            f"**Телефон:** `+{phone_number}`\n"
            f"**User ID:** `{user_id}`\n"
            f"**Роль:** {translate_role(role)}{bus_info}",
            reply_markup=user_delete_confirm_keyboard
        )
        
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при поиске пользователя для удаления: '{identifier}'")
        await send_message(message, "❌ Произошла ошибка! Не удалось найти пользователя.")
        await state.clear()

@router.callback_query(F.data == "user:delete:confirm", admin_filter())
async def cb_delete_user_confirm(query: CallbackQuery, state: FSMContext, user_manager: UserManager):
    data = await state.get_data()
    identifier_raw = data.get("identifier")
    name = data.get("name")
    
    try:
        identifier = normalize_identifier(identifier_raw)
        
        if validate_phone(identifier) and "+" in identifier_raw:
            await user_manager.delete_user(phone_number=identifier)
        else:
            await user_manager.delete_user(user_id=int(identifier))
        
        ConfigManager.log.logger.info(f"Администратор ID - {query.from_user.id} удалил пользователя {name}")
        await edit_message(
            query.message,
            f"✅ **Пользователь '{name}' успешно удален!**"
        )
        await state.clear()
        
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при удалении пользователя: '{identifier_raw}'")
        await edit_message(query.message, "❌ Произошла ошибка! Не удалось удалить пользователя.")
        await state.clear()

@router.callback_query(F.data == "user:delete:cancel", admin_filter())
async def cb_delete_user_cancel(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await edit_message(query.message, "↩️ Удаление пользователя отменено.")