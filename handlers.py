import re
from datetime import time
from aiogram import types, Dispatcher, Bot # Убрали Bot и Dispatcher, они здесь не нужны для получения scheduler
from aiogram.dispatcher import FSMContext

# Импорт из пакета db
from db import SessionLocal, User
# Импортируем обе клавиатуры
from keyboard import get_main_keyboard, get_cancel_keyboard
from config import logger
from states import ReminderStates
# НЕ импортируем add_or_update_reminder_job, remove_reminder_job из scheduler

# --- Обработчики Команд ---

async def start_handler(message: types.Message, state: FSMContext):
    """Обработчик команды /start. Регистрирует пользователя."""
    await state.finish() # Завершаем любое предыдущее состояние
    chat_id = str(message.chat.id)
    logger.info(f"/start от {chat_id}")
    session = SessionLocal() # Открываем сессию
    try:
        user = session.query(User).filter(User.chat_id == chat_id).first()
        if not user:
            # Если пользователя нет, создаем и добавляем
            session.add(User(chat_id=chat_id))
            session.commit() # Сохраняем изменения
            await message.reply("Привет! Зарегистрировал тебя. Установи время: /settime", reply_markup=get_main_keyboard())
        else:
            # Если пользователь есть
            await message.reply("Ты уже зарегистрирован!", reply_markup=get_main_keyboard())
    except Exception as e:
        # Простая обработка ошибок БД
        logger.error(f"Ошибка БД в /start для {chat_id}: {e}")
        await message.reply("Ошибка базы данных.")
    finally:
        # Гарантированно закрываем сессию
        session.close()

async def set_time_handler(message: types.Message, state: FSMContext):
    """Обработчик команды /settime. Переводит в состояние ожидания времени."""
    logger.info(f"/settime от {message.chat.id}")
    session = SessionLocal()
    try:
        # Проверяем, есть ли пользователь в БД
        user = session.query(User).filter(User.chat_id == str(message.chat.id)).first()
        if not user:
            # Если нет - просим зарегистрироваться
            await message.reply("Сначала зарегистрируйся: /start", reply_markup=get_main_keyboard())
            return # Выходим из функции
    finally:
        session.close()

    # Если пользователь есть, просим ввести время
    await message.reply("Введи время в формате ЧЧ:ММ (e.g., 10:30).\nИли /cancel для отмены.",
                       reply_markup=get_cancel_keyboard()) # Показываем кнопку Отмена
    await ReminderStates.waiting_for_time.set() # Устанавливаем состояние

async def help_handler(message: types.Message, state: FSMContext):
    """Обработчик команды /help."""
    await state.finish() # Сбрасываем состояние
    # Отправляем список команд
    await message.reply("Команды:\n/start\n/settime\n/status\n/stop\n/help\n/cancel", reply_markup=get_main_keyboard())

async def status_handler(message: types.Message, state: FSMContext):
    """Обработчик команды /status. Показывает статус."""
    await state.finish() # Сбрасываем состояние
    chat_id = str(message.chat.id)
    logger.info(f"/status от {chat_id}")
    session = SessionLocal()
    reply_text = "Не зарегистрирован (/start)" # Текст по умолчанию
    try:
        user = session.query(User).filter(User.chat_id == chat_id).first()
        if user:
            # Формируем строку времени или "Не установлено"
            time_str = user.reminder_time.strftime("%H:%M") if user.reminder_time else "Не установлено"
            reply_text = f"Статус: Зарегистрирован.\nВремя: {time_str}"
    except Exception as e:
        logger.error(f"Ошибка БД в /status для {chat_id}: {e}")
        reply_text = "Ошибка получения статуса."
    finally:
        session.close()
    # Отправляем результат
    await message.reply(reply_text, reply_markup=get_main_keyboard())

async def stop_handler(message: types.Message, state: FSMContext):
    """Обработчик команды /stop. Удаляет пользователя."""
    await state.finish() # Сбрасываем состояние
    chat_id = str(message.chat.id)
    logger.info(f"/stop от {chat_id}")
    session = SessionLocal()
    reply_text = "Ты и так не подписан." # Текст по умолчанию
    try:
        user = session.query(User).filter(User.chat_id == chat_id).first()
        if user:
            # НЕ вызываем remove_reminder_job, т.к. его нет
            session.delete(user) # Удаляем пользователя из БД
            session.commit() # Сохраняем изменения
            reply_text = "Отписал тебя от напоминаний."
            logger.info(f"Пользователь {chat_id} удален.")
    except Exception as e:
        logger.error(f"Ошибка БД в /stop для {chat_id}: {e}")
        reply_text = "Ошибка при отписке."
    finally:
        session.close()
    # Отправляем результат
    await message.reply(reply_text, reply_markup=get_main_keyboard())

async def cancel_handler(message: types.Message, state: FSMContext):
    """Обработчик команды /cancel. Отменяет состояние FSM."""
    current_state = await state.get_state() # Получаем текущее состояние
    if current_state is None:
        # Если состояния нет, то и отменять нечего
        await message.reply("Нет активного действия для отмены.", reply_markup=get_main_keyboard())
        return
    # Если состояние есть, отменяем его
    logger.info(f"Отмена состояния {current_state} для {message.chat.id}")
    await state.finish() # Завершаем состояние
    await message.reply("Действие отменено.", reply_markup=get_main_keyboard())

# --- Обработчик Состояния ---

async def process_time_handler(message: types.Message, state: FSMContext):
    """Обработчик для состояния waiting_for_time. Сохраняет время."""
    chat_id = str(message.chat.id)
    user_input = message.text.strip() # Получаем текст и убираем пробелы
    logger.info(f"Обработка времени '{user_input}' от {chat_id}")

    # Регулярное выражение для проверки формата ЧЧ:ММ
    time_pattern = r'^([01]\d|2[0-3]):([0-5]\d)$'

    if re.match(time_pattern, user_input): # Если формат верный
        session = SessionLocal()
        try:
            # Преобразуем строку в объект времени
            hours, minutes = map(int, user_input.split(':'))
            new_time = time(hour=hours, minute=minutes)

            # Находим пользователя в БД
            user = session.query(User).filter(User.chat_id == chat_id).first()
            if user: # Если нашли, обновляем время
                user.reminder_time = new_time
            else: # Если не нашли (маловероятно), создаем нового
                logger.warning(f"Пользователь {chat_id} не найден при обработке времени, создаем.")
                user = User(chat_id=chat_id, reminder_time=new_time)
                session.add(user)

            # НЕ вызываем add_or_update_reminder_job
            session.commit() # Сохраняем изменения в БД

            await message.reply(f"Время установлено на {user_input}", reply_markup=get_main_keyboard())
            await state.finish() # Завершаем состояние FSM
            logger.info(f"Время {user_input} установлено для {chat_id}")

        except Exception as e:
             logger.error(f"Ошибка БД при сохранении времени для {chat_id}: {e}")
             await message.reply("Ошибка сохранения времени.", reply_markup=get_main_keyboard())
             await state.finish() # Завершаем состояние при ошибке
        finally:
            session.close() # Закрываем сессию
    else:
        # Если формат времени неверный
        await message.reply("Неверный формат ЧЧ:ММ. Попробуй еще раз или /cancel.",
                           reply_markup=get_cancel_keyboard()) # Оставляем кнопку Отмена
        # Состояние НЕ завершаем, ждем правильного ввода или отмены

# --- Регистрация Обработчиков ---
def register_handlers(dp: Dispatcher):
    """Регистрирует все обработчики команд и состояний."""
    # Регистрируем команды (работают в любом состоянии - state='*')
    dp.register_message_handler(start_handler, commands=['start'], state='*')
    dp.register_message_handler(set_time_handler, commands=['settime'], state='*')
    dp.register_message_handler(help_handler, commands=['help'], state='*')
    dp.register_message_handler(status_handler, commands=['status'], state='*')
    dp.register_message_handler(stop_handler, commands=['stop'], state='*')
    dp.register_message_handler(cancel_handler, commands=['cancel'], state='*')

    # Регистрируем обработчик состояния (сработает только в состоянии waiting_for_time)
    dp.register_message_handler(process_time_handler, state=ReminderStates.waiting_for_time)

    logger.info("Обработчики успешно зарегистрированы.")