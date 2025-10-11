from aiogram import F, Router
from aiogram.types import Message

from core.managers import ConfigManager
from core.managers import UserManager
from utils.app import send_message


router = Router()

@router.message(F.contact)
async def get_contact(message: Message, user_manager: UserManager):
    contact = message.contact
    user_id = message.from_user.id
    phone_number = contact.phone_number.replace(' ', "").replace('+', "")

    if not contact.user_id or contact.user_id != user_id:
        await send_message(
            message,
            "❌ Вы можете отправить только свой контакт через кнопку в боте."
        )
        return

    try:
        get_user_id = await user_manager.get_parameters(
            phone_number=phone_number,
            get_user_id=True
        )

        if get_user_id == user_id:
            await send_message(message, "ℹ️ Вы уже зарегистрированы. Используйте команду /menu чтобы получить клавиатуру")
            return
        elif await user_manager.user_exists(phone_number=phone_number):
            await user_manager.set_user(phone_number=phone_number, new_user_id=user_id)
            await send_message(message, "✅ Готово! Вы успешно зарегистрированы. Используйте команду /menu чтобы получить клавиатуру")
            return

        await send_message(
            message,
            "❌ Ваши данные не найдены в базе. "
            "Пожалуйста, свяжитесь с администратором."
        )
        ConfigManager.log.logger.info(
            f"Пользователь с телефоном {phone_number} не найден. "
            f"Попытка входа user_id={user_id}."
        )

    except Exception as e:
        await send_message(
            message,
            text=f"❌ Произошла ошибка при проверке регистрации.",
            parse_mode=None
        )
        ConfigManager.log.logger.error(
            f"{e}\nОшибка при проверке регистрации. Номер: {phone_number}, user_id={user_id}"
        )


