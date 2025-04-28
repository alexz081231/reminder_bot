import os
import logging
from dotenv import load_dotenv

# --- Загрузка .env ---
load_dotenv() # Ищет .env в текущей директории или выше

# --- Telegram Bot Token ---
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не найдена! Добавьте ее в .env")

# --- Database Configuration ---
# ВАЖНО: Для MySQL база данных ДОЛЖНА БЫТЬ СОЗДАНА вручную!
# Формат URL для MySQL (mysqlclient): mysql+mysqlclient://user:password@host:port/dbname?charset=utf8mb4
# Формат URL для MySQL (PyMySQL):    mysql+pymysql://user:password@host:port/dbname?charset=utf8mb4
SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("Переменная окружения DATABASE_URL не найдена! Добавьте ее в .env (e.g., DATABASE_URL=mysql+mysqlclient://user:pass@host/db)")
elif 'mysql' not in SQLALCHEMY_DATABASE_URL:
     print(f"Предупреждение: DATABASE_URL ({SQLALCHEMY_DATABASE_URL}) не содержит 'mysql'. Убедитесь, что URL корректен.")


# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Конфигурация загружена.")
# Не логируем сам токен или пароли
logger.info(f"DATABASE_URL: {'******' if 'password@' in SQLALCHEMY_DATABASE_URL else SQLALCHEMY_DATABASE_URL}")