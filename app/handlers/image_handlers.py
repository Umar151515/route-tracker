from aiogram import F, Router, Bot
from aiogram.types import Message
from PIL import Image as PillowImage

from core.managers import UserManager
from core.managers import MessagesManager
from core.models import Image
from core.config import image_folder_path
from ..utils.messages import edit_message, delete_message
from ..utils.generate_response import response_generation
from utils.file_tools import generate_file_name


router = Router()

@router.message(F.photo)
async def photo_processing(
    message: Message, 
    bot: Bot, 
    user_manager: UserManager, 
    messages_manager: MessagesManager
):
    
    user = user_manager.get_user(message.from_user.id, True)

    try:
        upload_image_message = await message.reply("🖼️ Загрузка изображения...")
        
        file_name = generate_file_name()
        file = await bot.get_file(message.photo[-1].file_id)
        file_bytes = await bot.download_file(file.file_path)

        image = PillowImage.open(file_bytes)
        file_path = image_folder_path / f"{file_name}.png"
        image.save(file_path, format="PNG")
    except Exception as e:
        await edit_message(upload_image_message, f"{e}\n❌ Произошла ошибка при загрузке изображения.", None)
        return

    try:
        await edit_message(upload_image_message, "🔍 Обработка изображения...")

        image = Image(file_name)
        await image.generate_description()
        messages_manager.add_message(
            user.id,
            message.chat.id,
            "user", 
            image,
            message.message_id
        )
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        await edit_message(upload_image_message, f"{e}\n❌ Произошла ошибка при обработке изображения.", parse_mode=None)
        return

    if message.caption:
        messages_manager.add_message(
            user.id, 
            message.chat.id,
            "user", 
            message.caption,
            message.message_id
        )

        await delete_message(upload_image_message)
        await response_generation(message)
    else:
        await edit_message(upload_image_message, "✅ Фото успешно загружено в бота!")