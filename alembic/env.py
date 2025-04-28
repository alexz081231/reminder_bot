# alembic/env.py
import os # <-- Добавлен импорт os
import sys # <-- Добавлен импорт sys
from logging.config import fileConfig

# --- НАЧАЛО ИЗМЕНЕНИЙ: ПОРЯДОК ИМПОРТОВ И ПУТИ ---

# 1. Добавляем корневую папку проекта в путь Python *ПЕРЕД* импортом наших модулей
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# 2. Импортируем Base, URL и create_engine *ПОСЛЕ* настройки пути
try:
    from sqlalchemy import create_engine # <-- Добавлен импорт create_engine
    from db.database import Base  # Указываем путь к нашему Base
    from config import SQLALCHEMY_DATABASE_URL # Импортируем URL
except ImportError as e:
    print(f"Ошибка импорта в alembic/env.py: {e}")
    print("Убедитесь, что структура проекта и PYTHONPATH настроены верно.")
    print(f"Текущий sys.path: {sys.path}")
    sys.exit(1) # Выход, если не можем импортировать

# --- КОНЕЦ ИЗМЕНЕНИЙ: ПОРЯДОК ИМПОРТОВ И ПУТИ ---

from sqlalchemy import pool
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# --- НАЧАЛО ИЗМЕНЕНИЙ: УСТАНОВКА URL ПОСЛЕ ИМПОРТА ---

# 3. Устанавливаем URL базы данных в конфигурацию Alembic *ПОСЛЕ* его импорта
if SQLALCHEMY_DATABASE_URL:
    config.set_main_option('DB_URL', SQLALCHEMY_DATABASE_URL)
else:
    print("Ошибка: SQLALCHEMY_DATABASE_URL не найдена в config.py.")
    print("Убедитесь, что .env файл существует и содержит DATABASE_URL.")
    sys.exit(1)

# --- КОНЕЦ ИЗМЕНЕНИЙ: УСТАНОВКА URL ПОСЛЕ ИМПОРТА ---


# Interpret the config file for Python logging.
# This line sets up loggers basically.
# --- НАЧАЛО ИЗМЕНЕНИЙ: ПРОВЕРКА ФАЙЛА ЛОГОВ ---
if config.config_file_name is not None:
    # Проверяем, существует ли файл перед его использованием
    if os.path.exists(config.config_file_name):
         fileConfig(config.config_file_name)
    else:
         print(f"Предупреждение: Файл конфигурации логирования {config.config_file_name} не найден.")
# --- КОНЕЦ ИЗМЕНЕНИЙ: ПРОВЕРКА ФАЙЛА ЛОГОВ ---


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# --- НАЧАЛО ИЗМЕНЕНИЙ: УКАЗАНИЕ METADATA ---

# 4. Указываем Alembic на метаданные наших моделей
target_metadata = Base.metadata

# --- КОНЕЦ ИЗМЕНЕНИЙ: УКАЗАНИЕ METADATA ---

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    # ... (стандартные комментарии) ...
    """
    # --- НАЧАЛО ИЗМЕНЕНИЙ: ИСПРАВЛЕНИЕ OFFLINE ---
    # 5. Используем ТОЛЬКО ОДИН блок configure с правильными параметрами
    url = config.get_main_option("DB_URL") # Используем наш DB_URL
    context.configure(
        url=url,
        target_metadata=target_metadata, # Передаем наши метаданные
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True, # Добавлено для совместимости с MySQL
    )
    # --- КОНЕЦ ИЗМЕНЕНИЙ: ИСПРАВЛЕНИЕ OFFLINE ---

    # --- НАЧАЛО ИЗМЕНЕНИЙ: УДАЛЕНИЕ ДУБЛЯ ---
    # ВТОРОЙ БЛОК context.configure УДАЛЕН, ОН БЫЛ НЕПРАВИЛЬНЫМ
    # --- КОНЕЦ ИЗМЕНЕНИЙ: УДАЛЕНИЕ ДУБЛЯ ---

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    # ... (стандартные комментарии) ...
    """
    # --- НАЧАЛО ИЗМЕНЕНИЙ: ИСПРАВЛЕНИЕ ONLINE (Вариант 1 - Рекомендуемый) ---
    # 6. Используем create_engine напрямую с нашим URL
    # Это избегает проблем с интерполяцией и config.get_section
    connectable = create_engine(SQLALCHEMY_DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True, # Добавлено для совместимости с MySQL
            # compare_server_default=True, # Можно добавить при необходимости
        )

        with context.begin_transaction():
            context.run_migrations()
    # --- КОНЕЦ ИЗМЕНЕНИЙ: ИСПРАВЛЕНИЕ ONLINE ---


# Вызов функций остается прежним
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()