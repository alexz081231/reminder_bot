# db/database.py

import logging # Импортируем logging для возможной отладки
from sqlalchemy import create_engine, Column, String, Time
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError # Импорт для обработки ошибок SQLAlchemy

# Импортируем URL БД из конфигурации.
# Важно: Убедитесь, что config.py и .env загружаются до того,
# как этот модуль импортируется где-либо, где используется engine.
from config import SQLALCHEMY_DATABASE_URL, logger # Импортируем logger из config

# --- Подключение к базе данных ---
try:
    # Создаем SQLAlchemy engine
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        # pool_pre_ping=True # Опционально: проверять соединение перед использованием из пула
        # echo=False # Опционально: установить в True для логгирования всех SQL-запросов
    )
    # Создаем фабрику сессий
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # Создаем базовый класс для моделей
    Base = declarative_base()
    logger.info("SQLAlchemy engine и SessionLocal успешно созданы.")

except SQLAlchemyError as e:
    logger.critical(f"КРИТИЧЕСКАЯ ОШИБКА при создании SQLAlchemy engine или SessionLocal: {e}")
    # В реальном приложении здесь можно предпринять дополнительные действия или корректно завершить работу
    raise SystemExit(f"Ошибка подключения к БД: {e}")


# --- Модели SQLAlchemy ---

class User(Base):
    """
    Модель SQLAlchemy для таблицы пользователей.
    Хранит chat_id пользователя и установленное время напоминания.
    """
    __tablename__ = "users"

    # chat_id: Первичный ключ, идентификатор чата пользователя в Telegram.
    # VARCHAR(50) в MySQL, т.к. указана длина.
    chat_id = Column(String(50), primary_key=True)

    # reminder_time: Время для ежедневного напоминания.
    # Может быть NULL, если пользователь не установил время.
    # Тип TIME в MySQL.
    reminder_time = Column(Time, nullable=True)

    def __repr__(self):
        # Полезно для отладки: как объект будет представлен при печати
        time_str = self.reminder_time.strftime('%H:%M') if self.reminder_time else 'None'
        return f"<User(chat_id='{self.chat_id}', reminder_time='{time_str}')>"


# --- Создание таблиц (УПРАВЛЯЕТСЯ ЧЕРЕЗ ALEMBIC) ---

# Строка ниже должна быть ЗАКОММЕНТИРОВАНА или УДАЛЕНА,
# так как создание и обновление схемы БД управляется Alembic.
# Base.metadata.create_all(bind=engine)
logger.info("Автоматическое создание таблиц через Base.metadata.create_all отключено (управляется Alembic).")


# --- Функция для получения сессии БД ---

def get_db():
    """
    Зависимость (или просто функция) для получения сессии SQLAlchemy.
    Обеспечивает правильное открытие и закрытие сессии.
    """
    db = SessionLocal()
    try:
        yield db # Возвращаем сессию для использования
    except SQLAlchemyError as e:
        logger.error(f"Ошибка SQLAlchemy в сессии: {e}")
        # В зависимости от логики можно сделать db.rollback() здесь
        db.rollback() # Откатываем транзакцию при ошибке
        raise # Повторно вызываем исключение, чтобы его обработали выше
    finally:
        db.close() # Гарантированно закрываем сессию


# --- Экспорт основных компонентов ---

# Определяем, что будет доступно при импорте 'from db.database import *'
# (хотя лучше импортировать явно: from db.database import SessionLocal, User)
__all__ = [
    "Base",
    "SessionLocal",
    "User",
    "engine",
    "get_db", # Добавляем get_db в экспорт, если он будет использоваться извне
]