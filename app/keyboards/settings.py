from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.managers import ConfigManager
from core.models import User


main_settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Модель генерации текста', callback_data='text_models')],
    [InlineKeyboardButton(text='Модель генерации изображении', callback_data='image_models')],
])

def get_text_models_keyboard(user: User):
    text_models = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{model} {'✅' if model == user.text_model else ''}", 
                callback_data=f"select_text_model_{model}"
            )
        ] for model in ConfigManager.text.get_models()
    ])

    return text_models

def get_image_models_keyboard(user: User):
    image_models = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{model} {'✅' if model == user.image_model else ''}", 
                callback_data=f"select_image_model_{model}"
            )
        ] for model in ConfigManager.image.get_models()
    ])

    return image_models