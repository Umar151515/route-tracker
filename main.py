import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.handlers import routers
from app.core.services import UserService
from core.managers import UserManager
from core.managers import ConfigManager


async def main():
    bot = Bot(
        token=ConfigManager.env["TELEGRAM_BOT_TOKEN"],
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
 
    dp = Dispatcher()

    dp["user_service"] = UserService(bot)
    dp["user_manager"] = UserManager()

    for router in routers:
        dp.include_router(router)

    print("bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())