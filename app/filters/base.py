from aiogram.filters import BaseFilter
from aiogram.types import Message

from core.managers import ConfigManager
from core.managers import UserManager
from utils.app.message import send_message
from ..keyboards import phone_number_keyboard


async def check_user_exists(user_manager: UserManager, user_id: int, message: Message) -> bool:
    try:
        if await user_manager.user_exists(user_id=user_id):
            return True
    except Exception as e:
        await send_message(message, text=f"❌ Произошла ошибка при проверке регистрации.",)
        ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при проверке регистрации. ID пользователя: {user_id}")
        return False

    await send_message(
        message,
        text="Кажется, вы не зарегистрированы. Нажмите кнопку ниже, чтобы проверить вашу регистрацию по номеру телефона.",
        reply_markup=phone_number_keyboard
    )

    return False


class RoleFilter(BaseFilter):
    def __init__(self, role: str):
        self.role = role

    async def __call__(self, message: Message, user_manager: UserManager) -> bool:
        user_id = message.from_user.id

        if not await check_user_exists(user_manager, user_id, message):
            return False

        try:
            is_role = await user_manager.get_parameters(user_id=user_id, get_role=True) == self.role
        except Exception as e:
            await send_message(message, text=f"❌ Произошла ошибка при проверке роли.")
            ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при проверке роли.\nID пользователя: {user_id}\nРоль: {self.role}")
            return False
        
        return is_role
    

class ExistsFilter(BaseFilter):
    async def __call__(self, message: Message, user_manager: UserManager) -> bool:
        user_id = message.from_user.id
        is_exists = await check_user_exists(user_manager, user_id, message)
        return is_exists


def admin_filter():
    return RoleFilter("admin")

def driver_filter():
    return RoleFilter("driver")
