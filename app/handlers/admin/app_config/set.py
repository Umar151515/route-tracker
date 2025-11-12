from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from core.managers import ConfigManager
from ....keyboards.admin import get_app_config_set_keyboard
from ....states.admin import AdminAppConfigStates
from ....filters import admin_filter


router = Router()

@router.callback_query(F.data == "app_config:set", admin_filter())
async def cb_set_app_config_start(query: CallbackQuery, state: FSMContext):
    await state.set_state(AdminAppConfigStates.waiting_for_config_key)
    await query.message.edit_text(
        "⚙️ **Изменение настроек приложения**\n\n"
        "Выберите параметр для изменения:",
        reply_markup=get_app_config_set_keyboard()
    )

@router.callback_query(F.data.startswith("app_config:set_key:"), AdminAppConfigStates.waiting_for_config_key, admin_filter())
async def cb_set_app_config_key(query: CallbackQuery, state: FSMContext):
    config_key = query.data.split(":")[-1]
    
    await state.update_data(config_key=config_key)
    await state.set_state(AdminAppConfigStates.waiting_for_config_value)
    
    current_value = ConfigManager.app.get(config_key)
    
    await query.message.edit_text(
        f"⚙️ **Изменение параметра:** `{config_key}`\n"
        f"📋 **Текущее значение:** `{current_value}`\n\n"
        f"Введите новое значение:\n\n"
        f"*Для отмены отправьте 0*"
    )

@router.message(AdminAppConfigStates.waiting_for_config_value, admin_filter())
async def handle_set_app_config_value(message: Message, state: FSMContext):
    """Обработка нового значения конфига"""
    new_value = message.text.strip()
    
    if new_value == "0":
        await state.clear()
        await message.answer("↩️ Изменение конфигурации отменено.")
        return
    
    data = await state.get_data()
    config_key = data.get("config_key")
    
    try:
        ConfigManager.app.set(config_key, new_value)
        
        ConfigManager.log.logger.info(
            f"Администратор ID - {message.from_user.id} изменил параметр '{config_key}' на '{new_value}'"
        )
        
        await message.answer(
            f"✅ **Параметр успешно обновлен!**\n\n"
            f"**Параметр:** `{config_key}`\n"
            f"**Новое значение:** `{new_value}`"
        )
        await state.clear()
        
    except ValueError as e:
        error_msg = str(e)
        if "is not" in error_msg:
            expected_type = error_msg.split("'")[3]
            await message.answer(
                f"❌ **Неверный тип данных!**\n\n"
                f"Для параметра `{config_key}` ожидается тип: `{expected_type}`\n"
                f"Попробуйте ещё раз:"
            )
        else:
            await message.answer(
                f"❌ **Ошибка валидации!**\n\n{error_msg}\n\nПопробуйте ещё раз:"
            )
            
    except Exception as e:
        ConfigManager.log.logger.error(f"{e}\n❌ Ошибка при изменении параметра '{config_key}' на '{new_value}'")
        await message.answer(
            "❌ **Произошла ошибка!** Не удалось изменить параметр.\n\nПопробуйте ещё раз:"
        )