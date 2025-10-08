import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties

from app.handlers import routers
from core.managers import UserManager
from core.managers import BusStopsManager
from core.managers import ConfigManager
from core.managers import GoogleSheetsManager


async def main():
    bot = Bot(
        token=ConfigManager.env["TELEGRAM_BOT_TOKEN"],
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )

    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="menu", description="Показать главное меню"),
        BotCommand(command="my_details", description="Информация о мне"),
    ])
 
    dp = Dispatcher()

    dp["user_manager"] = await UserManager().create()
    dp["bus_stops_manager"] = await BusStopsManager().create()
    dp["sheets_manager"] = GoogleSheetsManager()
    for router in routers:
        dp.include_router(router)

    ConfigManager.log.logger.info("Bot launched")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())