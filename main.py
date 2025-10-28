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
from utils.text.processing import validate_phone, validate_name


async def setup_initial_admin(user_manager: UserManager):
    print("\n" + "="*50)
    print("ПЕРВОНАЧАЛЬНАЯ НАСТРОЙКА СИСТЕМЫ")
    print("="*50)
    print("Не обнаружено ни одного пользователя с ролью 'admin'.")
    print("Необходимо создать первого администратора системы.")
    print("="*50)
    
    while True:
        try:
            phone_number = input("\nВведите номер телефона администратора (формат: +996): ").strip().replace(' ', "").replace('+', "")
            
            if not validate_phone(phone_number):
                print("❌ Ошибка: Неверный формат номера телефона!")
                continue
            
            if await user_manager.user_exists(phone_number=phone_number):
                print("❌ Ошибка: Пользователь с таким номером телефона уже существует!")
                continue
            
            name = input("Введите имя администратора: ").strip()
            
            if not validate_name(name):
                print("❌ Ошибка: Неверный формат имени!")
                continue
            
            all_users = await user_manager.get_users()
            if any(user['name'] == name for user in all_users):
                print("❌ Ошибка: Пользователь с таким именем уже существует!")
                continue
            
            await user_manager.create_user(
                phone_number=phone_number,
                role="admin",
                name=name
            )
            
            print("\n✅ Администратор успешно создан!")
            print(f"Номер телефона: +{phone_number}")
            print(f"Имя: {name}")
            print("\nПервоначальная настройка завершена. Бот запускается...")
            break
            
        except ValueError as e:
            print(f"❌ Ошибка валидации: {e}")
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            print("Пожалуйста, попробуйте еще раз.")

async def check_and_setup_admin(user_manager: UserManager):
    all_users = await user_manager.get_users()
    admins = [user for user in all_users if user.get('role') == 'admin']
    
    if not admins:
        await setup_initial_admin(user_manager)

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

    user_manager = await UserManager().create()
    dp["user_manager"] = user_manager
    dp["bus_stops_manager"] = await BusStopsManager().create()
    dp["sheets_manager"] = GoogleSheetsManager()
    
    await check_and_setup_admin(user_manager)
    
    for router in routers:
        dp.include_router(router)

    ConfigManager.log.logger.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        ConfigManager.log.logger.info("Выход бота")