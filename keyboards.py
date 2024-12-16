from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

def main_kb():
    kb_list = [
        [KeyboardButton(text="\U0001F4C2Файл xlsx в csv"), KeyboardButton(text="\U0001F4C4Файл csv в xlsx")],
        [KeyboardButton(text="\U0001F4E5Завантажити CL"), KeyboardButton(text="\U00002194Замінити CL на власний")],
        [KeyboardButton(text="\U0001F9F9Очистити CL від дублікатів"), KeyboardButton(text="\U0001F5D1Очистити CL")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)
    return keyboard