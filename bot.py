from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import router
from db import init_db
from keep_alive import keep_alive

async def main():
    # Запускаем веб-сервер для предотвращения "засыпания" Glitch
    keep_alive()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
    ])

    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    print("Инициализация базы данных...")
    init_db()
    print("Запуск бота...")
    asyncio.run(main())
