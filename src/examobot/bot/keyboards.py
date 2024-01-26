from aiogram import types
from keyboard_texts import *
from src.examobot.bot.examobot2 import db_manager
from src.examobot.db.tables import *


def get_button(text, callback):
    return types.InlineKeyboardButton(text=text, callback_data=callback)


# AUTHOR'S KEYBOARDS #

def get_authors_buttons_():
    inline_keyboard = [
        [get_button(AUTHORS_CLASSROOMS_TEXT, AUTHORS_CLASSROOMS_CALLBACK)]
    ]
    return inline_keyboard


def get_classroom_keyboard(classrooms: list[Classroom]):
    inline_keyboard = [
        [get_button(classroom.title, f'{SPEC_CLASSROOM_CALLBACK}#{classroom.id}') for classroom in classrooms],
        [get_button(CREATE_CLASSROOM_TEXT, CREATE_CLASSROOM_CALLBACK)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# RESPONDENT'S KEYBOARDS #

def get_respondent_buttons_():
    inline_keyboard = [
        # will add
    ]
    return inline_keyboard


# COMMON KEYBOARDS #
def get_main_menu_keyboard():
    inline_keyboard = get_authors_buttons_() + get_respondent_buttons_()
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
