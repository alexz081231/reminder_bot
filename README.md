Хорошо, вот содержимое файла `README.md` для **упрощенной версии** проекта (с MySQL, папкой `db`, но без Redis и без продвинутого планировщика).

--- START OF FILE `README.md` ---
```markdown
# Telegram Reminder Bot (MySQL + Простой Scheduler)

Простой Telegram-бот для установки ежедневных напоминаний. Использует `aiogram`, `SQLAlchemy` с **MySQL** и базовый `APScheduler`.

**Примечание:** Эта версия является упрощенной. Состояния пользователя (например, при вводе времени) **не сохраняются** при перезапуске бота. Планировщик проверяет *всех* пользователей каждую минуту, что может быть неэффективно при большом их количестве. Для более надежных и производительных решений смотрите другие варианты кода, использующие Redis и индивидуальные задачи планировщика.

## ✨ Функциональность

-   Регистрация пользователей в базе данных MySQL.
-   Установка/изменение времени для ежедневных напоминаний.
-   Отправка напоминаний (простая проверка всех пользователей каждую минуту).
-   Просмотр текущего статуса и времени напоминания.
-   Отписка от напоминаний (удаление данных пользователя).
-   Использование `MemoryStorage` для хранения состояний диалогов (FSM) - **теряются при перезапуске**.
-   Логика базы данных вынесена в отдельный пакет `db`.
-   Конфигурация через файл `.env`.

## 🤖 Команды

-   `/start` - Запустить бота и зарегистрироваться.
-   `/settime` - Установить или изменить время ежедневного напоминания (формат ЧЧ:ММ).
-   `/status` - Показать ваше текущее установленное время напоминания.
-   `/stop` - Отписаться от напоминаний и удалить ваши данные.
-   `/help` - Показать список команд и описание.
-   `/cancel` - Отменить текущее действие (например, ввод времени).

## 🛠️ Установка и Запуск

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/your-username/telegram-reminder-bot.git # Замените на ваш URL
    cd telegram-reminder-bot
    ```

2.  **Настройте Базу Данных (MySQL):**
    *   Установите СУБД MySQL или MariaDB.
    *   **Создайте базу данных** для бота вручную, используя клиент MySQL:
        ```sql
        CREATE DATABASE bot_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        ```
        *(Замените `bot_db` на желаемое имя, если нужно)*
    *   **Создайте пользователя БД** и выдайте ему необходимые права на созданную базу данных:
        ```sql
        CREATE USER 'bot_user'@'localhost' IDENTIFIED BY 'your_strong_password';
        GRANT ALL PRIVILEGES ON bot_db.* TO 'bot_user'@'localhost';
        FLUSH PRIVILEGES;
        ```
        *(Замените `bot_user`, `your_strong_password` и `localhost` на ваши значения)*

3.  **Создайте и активируйте виртуальное окружение:**
    ```bash
    python3 -m venv venv # или python -m venv venv
    source venv/bin/activate  # для Linux/Mac
    # или
    # venv\Scripts\activate  # для Windows
    ```

4.  **Установите системные зависимости (если нужно):**
    *   Драйвер `mysqlclient` может потребовать инструменты сборки и заголовочные файлы MySQL.
        *   **Debian/Ubuntu:** `sudo apt-get update && sudo apt-get install build-essential python3-dev libmysqlclient-dev`
        *   **Fedora/CentOS:** `sudo dnf install gcc python3-devel mysql-devel`
        *   **macOS (Homebrew):** `brew install mysql`
    *   Если вы выбрали `PyMySQL`, этот шаг не требуется.

5.  **Установите Python зависимости:**
    ```bash
    pip install -r requirements.txt
    ```
    *Убедитесь, что в `requirements.txt` раскомментирован и установлен нужный драйвер для MySQL (`mysqlclient` или `PyMySQL`).*

6.  **Создайте и настройте файл `.env`:**
    *   Создайте файл `.env` в корне проекта.
    *   Добавьте токен вашего бота:
        ```dotenv
        BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi
        ```
    *   Добавьте **URL для подключения к MySQL**:
        ```dotenv
        # Используйте mysql+mysqlclient:// если установлен mysqlclient
        # Используйте mysql+pymysql:// если установлен PyMySQL
        DATABASE_URL=mysql+mysqlclient://bot_user:your_strong_password@localhost:3306/bot_db?charset=utf8mb4
        ```

7.  **Запустите бота:**
    ```bash
    python bot.py
    ```
    *Бот попытается создать таблицы в базе данных MySQL при первом запуске (если они еще не существуют).*

## 📁 Структура проекта

```
.
├── .env                # Конфигурация (токен, БД) - НЕ КОММИТИТЬ!
├── .gitignore          # Файлы, игнорируемые Git
├── bot.py              # Точка входа: инициализация, запуск
├── config.py           # Загрузка конфигурации из .env
├── db/                 # <-- Пакет для работы с базой данных
│   ├── __init__.py     # <-- Инициализатор пакета
│   └── database.py     # <-- Настройка SQLAlchemy, модель User
├── handlers.py         # Обработчики сообщений и команд
├── keyboard.py         # Функции для создания клавиатур
├── requirements.txt    # Список зависимостей Python
├── scheduler.py        # Простой планировщик (проверка каждую минуту)
├── states.py           # Определения состояний FSM
├── venv/               # Виртуальное окружение (в .gitignore)
└── README.md           # Этот файл документации
```

## 🔧 Зависимости

Основные зависимости перечислены в `requirements.txt`:

-   `aiogram`: Асинхронный фреймворк для Telegram ботов.
-   `SQLAlchemy`: ORM для работы с базами данных.
-   `APScheduler`: Библиотека для планирования задач.
-   `python-dotenv`: Для загрузки переменных окружения из `.env`.
-   `mysqlclient` или `PyMySQL`: Драйвер для работы с MySQL.
```
--- END OF FILE `README.md` ---