from aiogram.types import Message
from aiogram.enums import ParseMode

from utils.text.processing import split_text


async def send_message(
        message: Message, 
        text: str, 
        reply: bool = False, 
        parse_mode: ParseMode = ParseMode.MARKDOWN,
        **kwargs
    ) -> None:

    try:
        parts = split_text(text, 4096)
        
        if len(parts) > 1:
            parse_mode = None

        for part in parts:
            if reply:
                await message.reply(part, parse_mode=parse_mode, **kwargs)
            else:
                await message.answer(part, parse_mode=parse_mode, **kwargs)
    except Exception as e:
        if reply:
            await message.reply(f"{e}\n❌Произошла ошибка при отправке", parse_mode=parse_mode, **kwargs)
        else:
            await message.answer(f"{e}\n❌Произошла ошибка при отправке", parse_mode=parse_mode, **kwargs)

async def edit_message(
        message: Message, 
        text: str,
        parse_mode: ParseMode | None = ParseMode.MARKDOWN,
        **kwargs
    ) -> None:

    try:
        parts = split_text(text, 4096)
        
        if len(parts) > 1:
            parse_mode = None

        bot_message = await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=parts[0],
                parse_mode=parse_mode,
                **kwargs
            )
        
        if len(parts) > 1:
            await bot_message.reply(parts[1], parse_mode=None)
            for part in parts[2:]:
                await bot_message.answer(part, parse_mode=None)

    except Exception as e:
        if len(parts) > 1:
            await message.answer(f"{e}\n❌Произошла ошибка при отправке", parse_mode=parse_mode, **kwargs)
        else:
            await message.answer(f"{e}\n❌Произошла ошибка при редактировании", parse_mode=parse_mode, **kwargs)

async def delete_message(message: Message):
    try:
        await message.bot.delete_message(message.chat.id, message.message_id)
    except:
        pass