from aiogram import types
from aiogram.dispatcher import FSMContext
from database import SessionLocal, User
from keyboard import get_main_keyboard
from config import logger
from states import ReminderStates
import re
from datetime import time

# Обработчики команд
async def start_handler(message: types.Message, state: FSMContext):
    await state.finish()  # Сбрасываем состояние при любой команде
    logger.info(f"Получена команда /start от пользователя {message.from_user.id}")
    session = SessionLocal()
    chat_id = str(message.chat.id)
    
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if not user:
        session.add(User(chat_id=chat_id))
        session.commit()
        await message.reply("Привет! Ты зарегистрирован. Установи время напоминаний /settime.", 
                            reply_markup=get_main_keyboard())
    else:
        await message.reply("Ты уже зарегистрирован!", 
                            reply_markup=get_main_keyboard())
    session.close()

async def set_time_handler(message: types.Message, state: FSMContext):
    await message.reply("Введите время напоминания в формате ЧЧ:ММ (например, 10:30).\n"
                       "Или отправьте /cancel для отмены.", 
                        reply_markup=get_main_keyboard())
    await state.set_state(ReminderStates.waiting_for_time)

async def help_handler(message: types.Message, state: FSMContext):
    await state.finish()  # Сбрасываем состояние при любой команде
    await message.reply("Список команд:\n"
                        "/start - Запустить бота\n"
                        "/settime - Установить время напоминаний\n"
                        "/status - Проверить статус\n"
                        "/stop - Отключить напоминания\n"
                        "/cancel - Отменить текущее действие", 
                        reply_markup=get_main_keyboard())

async def status_handler(message: types.Message, state: FSMContext):
    await state.finish()  # Сбрасываем состояние при любой команде
    session = SessionLocal()
    user = session.query(User).filter_by(chat_id=str(message.chat.id)).first()
    
    if user:
        time_str = user.reminder_time.strftime("%H:%M") if user.reminder_time else "Не установлено"
        await message.reply(f"✅ Вы зарегистрированы.\nВремя напоминания: {time_str}", 
                            reply_markup=get_main_keyboard())
    else:
        await message.reply("❌ Вы не зарегистрированы.", 
                            reply_markup=get_main_keyboard())
    session.close()

async def stop_handler(message: types.Message, state: FSMContext):
    await state.finish()  # Сбрасываем состояние при любой команде
    session = SessionLocal()
    user = session.query(User).filter_by(chat_id=str(message.chat.id)).first()
    if user:
        session.delete(user)
        session.commit()
        await message.reply("Вы отписались от напоминаний. Возвращайтесь, если передумаете! 🫶", 
                            reply_markup=get_main_keyboard())
    else:
        await message.reply("Вы и так не подписаны на напоминания.", 
                            reply_markup=get_main_keyboard())
    session.close()

async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("Действие отменено.", reply_markup=get_main_keyboard())

async def process_time_handler(message: types.Message, state: FSMContext):
    # Проверка корректности введенного времени
    time_pattern = r'^([01]\d|2[0-3]):([0-5]\d)$'
    if re.match(time_pattern, message.text):
        session = SessionLocal()
        chat_id = str(message.chat.id)
        
        # Получаем часы и минуты
        hours, minutes = map(int, message.text.split(':'))
        
        # Обновляем или создаем пользователя с новым временем напоминания
        user = session.query(User).filter_by(chat_id=chat_id).first()
        if user:
            user.reminder_time = time(hour=hours, minute=minutes)
        else:
            user = User(chat_id=chat_id, reminder_time=time(hour=hours, minute=minutes))
            session.add(user)
        
        session.commit()
        session.close()
        
        await message.reply(f"✅ Время напоминания установлено на {message.text}", 
                            reply_markup=get_main_keyboard())
        await state.finish()
    else:
        await message.reply("❌ Неверный формат времени. Введите время в формате ЧЧ:ММ (например, 10:30).\n"
                          "Или отправьте /cancel для отмены.", 
                            reply_markup=get_main_keyboard()) 