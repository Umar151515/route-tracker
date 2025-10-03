from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, User

from app import keyboards
from core.managers import UserManager
from core.managers import ConfigManager
from ..core.services import UserService
from ..utils import send_message


router = Router()

@router.message(F.text)
async def register_passengers(message: Message, user_service: UserService):
    if not await user_service.check_user_role(message.from_user.id, "driver"):
        return
    
