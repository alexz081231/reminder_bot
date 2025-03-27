from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/start")],
            [KeyboardButton(text="/settime")],
            [KeyboardButton(text="/help")],
            [KeyboardButton(text="/status")],
            [KeyboardButton(text="/stop")]
        ],
        resize_keyboard=True
    )
    return keyboard 