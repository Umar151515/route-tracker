from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery

from core.managers import UserManager
from ..utils.messages import send_message, edit_message
from ..keyboards import main_settings, get_main_keyboard, get_text_models_keyboard, get_image_models_keyboard


router = Router()

@router.message(F.text == "⚙️ Настройки")
async def settings(message: Message, user_manager: UserManager):
    user = user_manager.get_user(message.from_user.id, True)

    settings_info = (
        "<b>⚙️ Настройки</b>\n\n"
        "<b>Текущие параметры:</b>\n"
        f"• Модель генерации текста: <code>{user.text_model}</code>\n"
        f"• Модель генерации изображений: <code>{user.image_model}</code>\n"
    )
    await send_message(message, settings_info, parse_mode=ParseMode.HTML, reply_markup=main_settings)

@router.message(F.text == "🌐 Выключить поиск в интернете ✅")
async def disable_web_search(message: Message, user_manager: UserManager):
    try:
        user_manager.create_user(message.from_user.id)
        user_manager.set_user(message.from_user.id, web_search=False)
        
        await send_message(message, "Поиск в интернете выключен", reply_markup=get_main_keyboard(False))
    except Exception as e:
        await send_message(message, f"{e}\n❌ Не удалось отключить поиск.", parse_mode=None)

@router.message(F.text == "🌐 Включить поиск в интернете ❌")
async def enable_web_search(message: Message, user_manager: UserManager):
    try:
        user_manager.create_user(message.from_user.id)
        user_manager.set_user(message.from_user.id, web_search=True)

        await send_message(message, "Поиск в интернете включён", reply_markup=get_main_keyboard(True))
    except Exception as e:
        await send_message(message, f"{e}\n❌ Не удалось включить поиск.", parse_mode=None)

@router.callback_query(F.data == "text_models")
async def text_model(callback: CallbackQuery, user_manager: UserManager):
    try:
        user = user_manager.get_user(callback.from_user.id, True)
        await edit_message(callback.message, "Выберите текстовую модель", reply_markup=get_text_models_keyboard(user))
    except Exception as e:
        await edit_message(callback.message, f"{e}\n❌ Произошла ошибка.", None)

@router.callback_query(F.data == "image_models")
async def image_model(callback: CallbackQuery, user_manager: UserManager):
    try:
        user = user_manager.get_user(callback.from_user.id, True)
        await edit_message(callback.message, "Выберите модель для генерации изображений", 
                           reply_markup=get_image_models_keyboard(user))
    except Exception as e:
        await edit_message(callback.message, f"{e}\n❌ Произошла ошибка.", None)
    
@router.callback_query(F.data.startswith("select_text_model_"))
async def handle_text_model_selection(callback: CallbackQuery, user_manager: UserManager):
    try:
        selected_model = callback.data.replace("select_text_model_", "")
        await edit_message(callback.message, f"Выбрана модель: {selected_model}")

        user_manager.create_user(callback.from_user.id)
        user_manager.set_user(callback.from_user.id, text_model=selected_model)

    except Exception as e:
        await edit_message(callback.message, f"{e}\n❌ Произошла ошибка.", None)
    
@router.callback_query(F.data.startswith("select_image_model_"))
async def handle_image_model_selection(callback: CallbackQuery, user_manager: UserManager):
    try:
        selected_model = callback.data.replace("select_image_model_", "")
        await edit_message(callback.message, f"Выбрана модель: {selected_model}")

        user_manager.create_user(callback.from_user.id)
        user_manager.set_user(callback.from_user.id, image_model=selected_model)

    except Exception as e:
        await edit_message(callback.message, f"{e}\n❌ Произошла ошибка.", None)