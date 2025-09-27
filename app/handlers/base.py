from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from app import keyboards
from core.managers import UserManager
from core.managers import ConfigManager
from ..utils.messages import send_message


router = Router()

@router.message(CommandStart())
async def start(message: Message, user_manager: UserManager):
    try:
        user = message.from_user
        user_manager.create_user(user.id)

        await send_message(
            message, 
            f"Привет, *{user.first_name}*!\nЯ бот для общения. Напиши мне что-нибудь, и я отвечу!", 
            reply_markup=keyboards.get_main_keyboard(
                         user_manager.get_parameters(user.id, web_search=True))
        )
    except Exception as e:
        await send_message(message, f"{e}\n❌ Произошла ошибка при запуске бота. Попробуйте снова.", parse_mode=None)

@router.message(F.text == "👤 Мой аккаунт")
async def enable_web_search(message: Message, user_manager: UserManager):
    try:
        user = user_manager.get_user(message.from_user.id, True)
        
        account_info = (
            "🔐 <b>Ваш аккаунт</b>\n\n"
            f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
            f"🌟 <b>Статус:</b> {user.status}\n\n"
            "📝 <b>Текстовые модели</b>\n"
            f"• Модель: <code>{user.text_model}</code>\n"
            f"• Инструмент: <code>{ConfigManager.text.selected_tool}</code>\n\n"
            "🖼️ <b>Изображения</b>\n"
            f"• Модель: <code>{user.image_model}</code>\n"
            f"• Инструмент: <code>{ConfigManager.image.selected_tool}</code>\n\n"
            f"🔢 <b>Оставшиеся запросы:</b> {user.requests_limit}" if user.status == "limited" else ""
        )

        await send_message(message, account_info, parse_mode=ParseMode.HTML)
    except Exception as e:
        await send_message(message, f"{e}\n❌ Не удалось получить информацию об аккаунте.", parse_mode=None)