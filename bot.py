from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import BOT_TOKEN, logger
from handlers import (
    start_handler, set_time_handler, help_handler,
    status_handler, stop_handler, process_time_handler,
    cancel_handler
)
from scheduler import setup_scheduler
from states import ReminderStates

# Инициализация бота с поддержкой состояний
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)

# Регистрация обработчиков команд с приоритетом
dp.register_message_handler(start_handler, commands=['start'], state='*')
dp.register_message_handler(set_time_handler, commands=['settime'], state='*')
dp.register_message_handler(help_handler, commands=['help'], state='*')
dp.register_message_handler(status_handler, commands=['status'], state='*')
dp.register_message_handler(stop_handler, commands=['stop'], state='*')
dp.register_message_handler(cancel_handler, commands=['cancel'], state='*')

# Регистрация обработчика состояния
dp.register_message_handler(process_time_handler, state=ReminderStates.waiting_for_time)

async def on_startup(dp: Dispatcher):
    scheduler = setup_scheduler(bot)
    dp['scheduler'] = scheduler

async def on_shutdown(dp: Dispatcher):
    scheduler = dp['scheduler']
    scheduler.shutdown()

if __name__ == '__main__':
    logger.info("Запуск программы...")
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)