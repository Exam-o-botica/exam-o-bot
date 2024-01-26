from aiogram import types
from keyboard_texts import *


def get_button(text, callback):
    return types.InlineKeyboardButton(text=text, callback_data=callback)


def get_start_keyboard() -> types.InlineKeyboardMarkup:
    inline_keyboard = [
        [get_button(STUDENT_TEXT, STUDENT_CALLBACK)],
        [get_button(TEACHER_TEXT, TEACHER_CALLBACK)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
