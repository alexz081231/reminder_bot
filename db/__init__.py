# db/__init__.py

"""
Пакет для работы с базой данных.
Экспортирует основные компоненты SQLAlchemy.
"""
# Убираем create_db_tables из этой строки импорта:
from .database import Base, SessionLocal, User, engine #, create_db_tables <-- УДАЛЕНО

# Определяем, что будет импортировано при `from db import *`
# Убираем create_db_tables из этого списка:
__all__ = [
    "Base",
    "SessionLocal",
    "User",
    "engine",
    # "create_db_tables",  <-- УДАЛЕНО
]

# Можно добавить логгирование при инициализации пакета, если нужно
# from ..config import logger
# logger.info("Пакет 'db' инициализирован.")