from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
# Используем MemoryStorage вместо Redis
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Импорт конфигурации и компонентов
from config import BOT_TOKEN, logger
from handlers import register_handlers
from scheduler import setup_scheduler
# НЕ импортируем create_db_tables из db
# from db import create_db_tables # <--- ЭТА СТРОКА УДАЛЕНА/ЗАКОММЕНТИРОВАНА

async def on_startup(dp: Dispatcher):
    """Выполняется при запуске бота."""
    logger.info("----- Запуск Бота -----")

    # 1. НЕ вызываем create_db_tables
    # Предполагается, что таблицы в MySQL созданы вручную или другим способом.
    logger.info("Пропуск автоматического создания таблиц БД.")
    # При необходимости можно добавить проверку соединения с БД здесь,
    # импортировав engine из db
    # from db import engine
    # try:
    #     with engine.connect() as connection:
    #         logger.info("Проверка соединения с БД в on_startup прошла успешно.")
    # except Exception as e:
    #     logger.critical(f"КРИТИЧЕСКАЯ ОШИБКА проверки соединения с БД: {e}")
    #     raise SystemExit(f"Не удалось подключиться к БД при старте: {e}")


    # 2. Настраиваем и запускаем планировщик
    try:
        scheduler: AsyncIOScheduler = setup_scheduler(dp.bot)
        # Сохраняем планировщик для доступа (хотя в этом варианте он не нужен в хэндлерах)
        dp['scheduler'] = scheduler
    except Exception as e:
        logger.critical(f"КРИТИЧЕСКАЯ ОШИБКА при настройке планировщика: {e}.")
        raise SystemExit(f"Не удалось настроить планировщик: {e}")

    logger.info("----- Бот Запущен -----")


async def on_shutdown(dp: Dispatcher):
    """Выполняется при остановке бота."""
    logger.info("----- Остановка Бота -----")
    # Останавливаем планировщик
    scheduler: AsyncIOScheduler = dp.get('scheduler')
    if scheduler and scheduler.running:
        try:
            scheduler.shutdown(wait=False) # Быстро останавливаем
            logger.info("Планировщик остановлен.")
        except Exception as e:
            logger.error(f"Ошибка при остановке планировщика: {e}")
    # MemoryStorage не требует закрытия
    logger.info("----- Бот Остановлен -----")


def main():
    """Основная функция запуска."""
    logger.info("Инициализация...")

    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    # Используем MemoryStorage
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    # Регистрация обработчиков
    register_handlers(dp)

    # Запуск поллинга
    logger.info("Запуск polling...")
    executor.start_polling(
        dispatcher=dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit) as e:
        logger.warning(f"Завершение работы: {e}")
    except Exception as e:
        logger.critical(f"Необработанная ошибка: {e}", exc_info=True)