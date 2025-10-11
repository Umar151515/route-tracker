from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from core.managers import UserManager, ConfigManager
from utils.text.processing import validate_phone, normalize_identifier, format_user_record
from ....utils import send_message
from ....keyboards.admin import get_user_edit_fields_keyboard
from ....states.admin import AdminUserEditStates
from ....filters import admin_filter


router = Router()

@router.message(F.text.regexp(r"^\+?\d{3,30}$"), admin_filter())
async def auto_user_lookup(message: Message, user_manager: UserManager, state: FSMContext):
    identifier = normalize_identifier(message.text)
    
    try:
        user = None
        if validate_phone(identifier) and "+" in message.text:
            user = await user_manager.get_parameters(phone_number=identifier, get_role=True, get_name=True, get_bus_number=True)
            user_id = await user_manager.get_parameters(phone_number=identifier, get_user_id=True)
            phone_number = identifier
        elif identifier.isdigit():
            user = await user_manager.get_parameters(user_id=int(identifier), get_role=True, get_name=True, get_bus_number=True)
            user_id = int(identifier)
            phone_number = await user_manager.get_parameters(user_id=user_id, get_phone_number=True)

        if not user:
            await send_message(message, "🤷‍♂️ Пользователь не найден.")
            return

        role, name, bus_number = user

        await send_message(
            message, 
            f"**👤 Пользователь найден:**\n\n"
            f"{format_user_record(name, role, phone_number, user_id, bus_number)}"
            "\nВыберите действие:",
            reply_markup=get_user_edit_fields_keyboard(role)
        )

        await state.update_data(identifier=message.text)
        await state.set_state(AdminUserEditStates.waiting_for_field)

    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Произошла Ошибка при автоподстановке пользователя.")
        await send_message(message, "❌ Произошла ошибка при поиске пользователя.")