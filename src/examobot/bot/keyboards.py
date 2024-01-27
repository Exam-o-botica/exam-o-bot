from aiogram import types
from keyboard_texts import *
from src.examobot.db.tables import *


def get_button(text, callback):
    return types.InlineKeyboardButton(text=text, callback_data=callback)


BACK_TO_MAIN_MENU_BTN = get_button(BACK_TO_MAIN_MENU_TEXT, BACK_TO_MAIN_MENU_CALLBACK)
GO_TO_MAIN_MENU_BTN = get_button(GO_TO_MAIN_MENU_TEXT, BACK_TO_MAIN_MENU_CALLBACK)


# AUTHOR'S KEYBOARDS #

def get_authors_buttons_():
    inline_keyboard = [
        [get_button(AUTHORS_CLASSROOMS_TEXT, AUTHORS_CLASSROOMS_CALLBACK)],
        [get_button(AUTHORS_TESTS_TEXT, AUTHORS_TESTS_CALLBACK)],
    ]
    return inline_keyboard


def get_classroom_keyboard(classrooms: list[Classroom]):
    classrooms_list = []
    for classroom in classrooms:
        classrooms_list.append([get_button(classroom.title, f'{SPEC_CLASSROOM_CALLBACK}#{classroom.id}')])
    inline_keyboard = [
        *classrooms_list,
        [get_button(CREATE_CLASSROOM_TEXT, CREATE_CLASSROOM_CALLBACK)],
        [BACK_TO_MAIN_MENU_BTN],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_tests_keyboard(tests: list[Test]):
    tests_list = []
    for test in tests:
        tests_list.append([get_button(test.title, f'{SPEC_TEST_CALLBACK}#{test.id}')])
    inline_keyboard = [
        *tests_list,
        [get_button(CREATE_TEST_TEXT, CREATE_TEST_CALLBACK)],
        [BACK_TO_MAIN_MENU_BTN],
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


def get_go_to_main_menu_keyboard():
    inline_keyboard = [
        [GO_TO_MAIN_MENU_BTN],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
