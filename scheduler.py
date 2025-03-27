from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from database import SessionLocal, User
from config import logger
from aiogram import Bot
from keyboard import get_main_keyboard
from datetime import datetime, time
from sqlalchemy import extract

async def send_reminder(bot: Bot):
    logger.info("Запуск функции send_reminder")
    session = SessionLocal()
    
    # Получаем текущее время
    current_time = datetime.now().time()
    current_hour = current_time.hour
    current_minute = current_time.minute
    logger.info(f"Текущее время: {current_hour:02d}:{current_minute:02d}")
    
    # Находим пользователей с совпадающим временем напоминания
    users = session.query(User).filter(
        User.reminder_time.isnot(None),
        extract('hour', User.reminder_time) == current_hour,
        extract('minute', User.reminder_time) == current_minute
    ).all()
    
    logger.info(f"Найдено пользователей для напоминания: {len(users)}")
    
    for user in users:
        try:
            logger.info(f"Отправка напоминания пользователю {user.chat_id}")
            await bot.send_message(user.chat_id, "Не забудь поработать! 🌟", 
                                   reply_markup=get_main_keyboard())
            logger.info(f"Напоминание успешно отправлено пользователю {user.chat_id}")
        except Exception as e:
            logger.error(f"Ошибка при отправке напоминания пользователю {user.chat_id}: {e}")
    session.close()

def setup_scheduler(bot: Bot):
    logger.info("Настройка планировщика")
    scheduler = AsyncIOScheduler()
    
    # Добавляем задачу для проверки каждую минуту
    job = scheduler.add_job(send_reminder, 'cron', minute='*', args=[bot])
    logger.info("Задача добавлена в планировщик")
    
    # Запускаем планировщик
    scheduler.start()
    logger.info("Планировщик запущен")
    
    # Выводим информацию о следующем запуске
    if job and job.next_run_time:
        logger.info(f"Следующий запуск запланирован на: {job.next_run_time}")
    
    return scheduler 