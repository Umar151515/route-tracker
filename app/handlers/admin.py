from aiogram import F, Router
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, ContentType, User

from core.managers import ConfigManager
from core.managers import UserManager
from ..utils import send_message, edit_message
from ..keyboards import user_settings_keyboard, bus_settings_keyboard, sheets_settings_keyboard
from ..filters import admin_filter


router = Router()

@router.message(F.text == "👤 Настройки пользователей", admin_filter())
async def user_settings(message: Message):
    await send_message(message, "Выберите опцию", reply_markup=user_settings_keyboard)

@router.message(F.text == "🚌 Настройки автобусов", admin_filter())
async def bus_settings(message: Message):
    await send_message(message, "Выберите опцию", reply_markup=bus_settings_keyboard)

@router.message(F.text == "📄 Настройки гугл таблицы", admin_filter())
async def user_settings(message: Message):
    await send_message(message, "Выберите опцию", reply_markup=sheets_settings_keyboard)


@router.callback_query(F.data == "user:get_info", admin_filter())
async def user_info(message: Message):
    user_id = message.from_user.id
    
    
    