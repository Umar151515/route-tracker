from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from utils.text.processing import split_text
from core.managers import ConfigManager


async def send_message(
        message: Message, 
        text: str, 
        reply: bool = False, 
        parse_mode: ParseMode = ParseMode.MARKDOWN,
        **kwargs
    ) -> None:

    parts = split_text(text, 4096)

    initial_parse_mode = parse_mode
    
    for i, part in enumerate(parts):
        current_parse_mode = initial_parse_mode if i == 0 and len(parts) == 1 else None
        
        try:
            if reply:
                await message.reply(part, parse_mode=current_parse_mode, **kwargs)
            else:
                await message.answer(part, parse_mode=current_parse_mode, **kwargs)
        
        except TelegramBadRequest as e:
            ConfigManager.log.logger.warning(f"Ошибка парсинга в сообщении (попытка 1). Переотправка без parse_mode. {e}")
            
            try:
                if reply:
                    await message.reply(part, parse_mode=None, **kwargs)
                else:
                    await message.answer(part, parse_mode=None, **kwargs)
            
            except Exception as e_retry:
                ConfigManager.log.logger.error(f"{e_retry}\n❌ Критическая ошибка при отправке (попытка 2). ID: {message.from_user.id}\nТекст (часть {i+1}): {part}")
                if reply:
                    await message.reply(f"❌ Произошла ошибка при отправке", parse_mode=None)
                else:
                    await message.answer(f"❌ Произошла ошибка при отправке", parse_mode=None)
                break 

        except Exception as e:
            ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при отправке. ID: {message.from_user.id}\nТекст (часть {i+1}): {part}")
            if reply:
                await message.reply(f"❌ Произошла ошибка при отправке", parse_mode=None)
            else:
                await message.answer(f"❌ Произошла ошибка при отправке", parse_mode=None)
            break

async def send_message_from_id(
        bot: Bot,
        user_id: int,
        text: str,
        parse_mode: ParseMode = ParseMode.MARKDOWN,
        **kwargs
    ):

    parts = split_text(text, 4096)
    initial_parse_mode = parse_mode
    
    for i, part in enumerate(parts):
        current_parse_mode = initial_parse_mode if i == 0 and len(parts) == 1 else None

        try:
            await bot.send_message(user_id, part, parse_mode=current_parse_mode, **kwargs)
        
        except TelegramBadRequest as e:
            ConfigManager.log.logger.warning(f"Ошибка парсинга при отправке по ID (попытка 1). Переотправка без parse_mode. {e}")
            
            try:
                await bot.send_message(user_id, part, parse_mode=None, **kwargs)
            
            except Exception as e_retry:
                ConfigManager.log.logger.error(f"{e_retry}\n❌ Критическая ошибка при отправке по ID (попытка 2). ID: {user_id}\nТекст (часть {i+1}): {part}")
                await bot.send_message(user_id, f"❌ Произошла ошибка при отправке", parse_mode=None)
                break

        except Exception as e:
            ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при отправке по ID. ID: {user_id}\nТекст (часть {i+1}): {part}")
            await bot.send_message(user_id, f"❌ Произошла ошибка при отправке", parse_mode=None)
            break

async def edit_message(
        message: Message, 
        text: str,
        parse_mode: ParseMode | None = ParseMode.MARKDOWN,
        **kwargs
    ) -> None:

    parts = split_text(text, 4096)
    initial_parse_mode = parse_mode
    
    try:
        bot_message = await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=parts[0],
                parse_mode=initial_parse_mode,
                **kwargs
            )
        
        if len(parts) > 1:
            await bot_message.reply(parts[1], parse_mode=None)
            for part in parts[2:]:
                await bot_message.answer(part, parse_mode=None)
    
    except TelegramBadRequest as e:
        ConfigManager.log.logger.warning(f"Ошибка парсинга при редактировании (попытка 1). Перередактирование без parse_mode. {e}")
        
        try:
            bot_message = await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=parts[0],
                parse_mode=None,
                **kwargs
            )

            if len(parts) > 1:
                await bot_message.reply(parts[1], parse_mode=None)
                for part in parts[2:]:
                    await bot_message.answer(part, parse_mode=None)

        except Exception as e_retry:
            ConfigManager.log.logger.error(f"{e_retry}\n❌ Критическая ошибка при редактировании (попытка 2). ID: {message.from_user.id}\nТекст (часть 1): {parts[0]}")
            await message.answer(f"❌ Произошла критическая ошибка при редактировании", parse_mode=None)

    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Произошла ошибка при редактировании. ID: {message.from_user.id}\nТекст (часть 1): {parts[0]}")
        await message.answer(f"❌ Произошла ошибка при редактировании", parse_mode=None)

async def delete_message(message: Message):
    try:
        await message.bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        ConfigManager.log.logger.debug(f"Не удалось удалить сообщение. {e}")