from aiogram import Bot

from ...keyboards import phone_number_keyboard
from ...utils import send_message_from_id
from core.managers import ConfigManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.managers import UserManager


class UserService:
    def __init__(self, bot: Bot, user_manager: UserManager):
        self.bot = bot
        self.user_manager = user_manager
    
    async def check_user_exists(self, user_id: int) -> bool:
        try:
            if await self.user_manager.user_exists(user_id=user_id):
                return True
        except Exception as e:
            await send_message_from_id(
                self.bot,
                user_id,
                text=f"{e}\n❌ Произошла ошибка при проверке регистрации.",
                parse_mode=None
            )
            ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при проверке регистрации. ID пользователя: {user_id}")
            return False

        await send_message_from_id(
            self.bot,
            user_id,
            text="Кажется, вы не зарегистрированы. Нажмите кнопку ниже, чтобы проверить вашу регистрацию по номеру телефона.",
            reply_markup=phone_number_keyboard
        )

        return False
    
    async def check_user_role(self, user_id: int, desired_role: str) -> bool:
        if not await self.check_user_exists(user_id):
            return False

        try:
            is_role = await self.user_manager.get_parameters(user_id=user_id, get_role=True) == desired_role
        except Exception as e:
            await send_message_from_id(
                self.bot,
                user_id,
                text=f"{e}\n❌ Произошла ошибка при проверке роли.",
                parse_mode=None
            )
            ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при проверке роли.\nID пользователя: {user_id}\nРоль: {desired_role}")
            return False
        
        return is_role