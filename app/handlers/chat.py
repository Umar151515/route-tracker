from aiogram import F, Router
from aiogram.types import Message

from core.managers import UserManager
from core.managers import MessagesManager
from ..core.services import UserService
from ..utils.messages import send_message
from ..utils.generate_response import response_generation


router = Router()

@router.message(F.text == "🗑️ Очистить чат")
async def clear_chat(message: Message, user_manager: UserManager, messages_manager: MessagesManager):
    try:
        user_manager.create_user(message.from_user.id)
        messages_manager.clear_messages(message.from_user.id, message.chat.id)
        messages_manager.set_system_prompt(
            message.from_user.id, 
            message.chat.id, 
            user_manager.get_parameters(message.from_user.id, role_model=True)
        )

        await send_message(message, f"🧹Чат очищен")
    except Exception as e:
        await send_message(message, f"{e}\n❌ Не удалось очистить чат.", parse_mode=None)

@router.message(F.text == "🔍 История чата")
async def chat_history(message: Message, user_manager: UserManager, messages_manager: MessagesManager):
    try:
        if not user_manager.get_user(message.from_user.id):
            welcome_msg = (
                "👋 Привет, {name}! Я вижу, ты здесь впервые.\n\n"
                "Твоя история сообщений пока пуста. Давай начнём общение! 😊"
            ).format(name=message.from_user.full_name)
            await send_message(message, welcome_msg)

            user_manager.create_user(message.from_user.id)
            return
        messages = messages_manager.get_messages(message.from_user.id, message.chat.id).get_list()
        messages_text = ""

        for message_dict in messages:
            messages_text += f"{message_dict["role"]}: {message_dict["content"]}\n\n"

        if messages_text:
            await send_message(message, messages_text, parse_mode=None)
        else:
            await send_message(message, "Твоя история сообщений пока пуста. Давай начнём общение!")
    except Exception as e:
        await send_message(message, f"{e}\n❌ Не удалось отправить историю чата.", parse_mode=None)


@router.message(F.text)
async def handle_text_message(
    message: Message, 
    user_manager: UserManager, 
    messages_manager: MessagesManager,
    user_service: UserService
):
    
    try:
        user = user_manager.get_user(message.from_user.id, True)
        messages_manager.add_message(
            user.id, 
            message.chat.id, 
            "user", 
            f"{await user_service.get_full_name(user.id)}: {message.text}", 
            message.message_id
        )

        await response_generation(message)
    except Exception as e:
        await send_message(message, f"{e}\n❌ Произошла ошибка при генерации ответа.", True, None)