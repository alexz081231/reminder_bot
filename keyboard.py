from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Основная клавиатура."""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("/start"), KeyboardButton("/help"))
    keyboard.add(KeyboardButton("/settime"), KeyboardButton("/status"))
    keyboard.add(KeyboardButton("/stop"))
    return keyboard

# --- ВОТ ЭТУ ФУНКЦИЮ НУЖНО ДОБАВИТЬ/ВЕРНУТЬ ---
def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура отмены."""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("/cancel"))
    return keyboard
# --- КОНЕЦ ДОБАВЛЕНИЯ ---