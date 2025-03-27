# Telegram Reminder Bot

Бот для отправки напоминаний в указанное время через Telegram.

## Функциональность

- Регистрация пользователей
- Установка времени напоминаний
- Отправка напоминаний в указанное время
- Просмотр статуса и текущих настроек
- Отмена подписки на напоминания

## Команды

- `/start` - Запустить бота
- `/settime` - Установить время напоминаний
- `/help` - Показать список команд
- `/status` - Проверить статус
- `/stop` - Отключить напоминания
- `/cancel` - Отменить текущее действие

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/telegram-reminder-bot.git
cd telegram-reminder-bot
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` и добавьте в него токен бота:
```
BOT_TOKEN=your_bot_token_here
```

5. Запустите бота:
```bash
python bot.py
```

## Структура проекта

```
├── bot.py              # Основной файл бота
├── config.py           # Конфигурация
├── database.py         # Работа с базой данных
├── handlers.py         # Обработчики команд
├── keyboard.py         # Клавиатуры
├── scheduler.py        # Планировщик напоминаний
├── states.py           # Состояния FSM
├── requirements.txt    # Зависимости
└── README.md          # Документация
```

## Лицензия

MIT 