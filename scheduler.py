from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import extract # Для извлечения часа/минуты
from datetime import datetime, time

# Импорт из пакета db и config
from db import SessionLocal, User
from config import logger
from aiogram import Bot
from keyboard import get_main_keyboard

async def send_reminder(bot: Bot):
    """Проверяет пользователей и отправляет напоминания (запускается каждую минуту)."""
    logger.debug("Запуск проверки напоминаний scheduler'ом...")
    session = SessionLocal()
    try:
        current_time = datetime.now().time()
        current_hour = current_time.hour
        current_minute = current_time.minute

        # Находим пользователей с совпадающим временем (не очень эффективно)
        users_to_remind = session.query(User).filter(
            User.reminder_time.isnot(None),
            extract('hour', User.reminder_time) == current_hour,
            extract('minute', User.reminder_time) == current_minute
        ).all()

        if users_to_remind:
            logger.info(f"Найдено пользователей для напоминания ({len(users_to_remind)}) в {current_hour:02d}:{current_minute:02d}")
            for user in users_to_remind:
                try:
                    await bot.send_message(user.chat_id, "Не забудь поработать! 🌟",
                                           reply_markup=get_main_keyboard())
                    logger.info(f"Напоминание отправлено пользователю {user.chat_id}")
                except Exception as e:
                    # Простая обработка ошибок отправки
                    logger.error(f"Ошибка отправки напоминания {user.chat_id}: {e}")
                    # Здесь можно добавить логику удаления пользователя/задачи при BotBlocked, но код станет сложнее
    except Exception as e:
         logger.error(f"Ошибка в функции send_reminder: {e}")
    finally:
        session.close()


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """Настраивает и запускает планировщик."""
    logger.info("Настройка планировщика...")
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow") # Укажите ваш часовой пояс!

    # Добавляем одну задачу - проверять каждую минуту
    scheduler.add_job(send_reminder, 'cron', minute='*', args=[bot])
    logger.info("Задача ежеминутной проверки добавлена.")

    try:
        scheduler.start()
        logger.info("Планировщик запущен.")
    except Exception as e:
        logger.error(f"Ошибка запуска планировщика: {e}")
        raise

    return scheduler