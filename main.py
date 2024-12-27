import asyncio
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from handlers import read_answers, admin_actions, user_handlers
from config import config
from handlers.admin_actions import moderation_cycle

# Функция конфигурирования и запуска бота
async def main():
    
    bot = Bot(token=config.BOT_TOKEN)
    config.bot = bot
    # Загружаем конфиг в переменную config
    # config: Config = load_config()
    
    # Инициализируем бот и диспетчер
        # тут ещё много других интересных настроек
    dp = Dispatcher()
    # Регистриуем роутеры в диспетчере
    dp.include_router(user_handlers.router)
    dp.include_router(admin_actions.router)
    dp.include_router(read_answers.router)
    config.dp = dp
    # for user_id in database.select_all_params_from_table_in_dict(Users):
    #     await config.bot.send_message(chat_id=user_id, text="Бот был перезапущен. Если у вас было включено отслеживание коэффициентов приемки, пожалуйста, повторите команду. Приносим извинения за доставленные неудобства.")
    # Пропускаем накопившиеся апдейты и запускаем polling
    await config.bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(config.bot, allowed_updates=dp.resolve_used_update_types())
    
async def main_launcher():
    bot = asyncio.create_task(main())
    # bot = Bot(token=config.BOT_TOKEN)
    # config.bot = bot
    # dp = Dispatcher()
    # config.dp = dp
    coefficients = asyncio.create_task(moderation_cycle())
    
    await bot
    await coefficients

asyncio.run(main_launcher())