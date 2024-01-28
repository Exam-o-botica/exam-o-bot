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


def get_created_classrooms_keyboard(classrooms: list[Classroom]):
    classrooms_list = []
    for classroom in classrooms:
        classrooms_list.append([get_button(classroom.title, f'{SPEC_CREATED_CLASSROOM_CALLBACK}#{classroom.id}')])
    inline_keyboard = [
        *classrooms_list,
        [get_button(CREATE_CLASSROOM_TEXT, CREATE_CLASSROOM_CALLBACK)],
        [BACK_TO_MAIN_MENU_BTN],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_emoji_test_status(status: TestStatus):
    if status == TestStatus.AVAILABLE:
        return '🟢'
    else:
        return '🔴'


def get_created_tests_keyboard(tests: list[Test]):
    tests_list = []
    for test in tests:
        tests_list.append([get_button(f"{test.title} {get_emoji_test_status(test.status_set_by_author)}",
                                      f'{SPEC_CREATED_TEST_CALLBACK}#{test.id}')])
    inline_keyboard = [
        *tests_list,
        [get_button(CREATE_TEST_TEXT, CREATE_TEST_CALLBACK)],
        [BACK_TO_MAIN_MENU_BTN],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_spec_created_test_keyboard(test: Test):
    inline_keyboard = [
        [get_button(CLOSE_TEST_TEXT, f"{CLOSE_TEST_CALLBACK}#{test.id}")],
        [get_button(REFRESH_TEST_DATA_TEXT, f"{REFRESH_TEST_DATA_CALLBACK}#{test.id}")],
        [get_button(EDIT_TEST_TEXT, f"{EDIT_TEST_CALLBACK}#{test.id}")],
        [get_button(SHARE_TEST_LINK_TEXT, f"{SHARE_TEST_LINK_CALLBACK}#{test.id}")],
        [get_button(GO_TO_PREVIOUS_MENU_TEXT, AUTHORS_TESTS_CALLBACK)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_share_test_link_keyboard(test_id: int):
    inline_keyboard = [
        [get_button(SHARE_TEST_LINK_TO_CLASSROOM_TEXT, f'{SHARE_TEST_LINK_TO_CLASSROOM_CALLBACK}#{test_id}')],
        [get_button(GO_TO_PREVIOUS_MENU_TEXT, f'{SPEC_CREATED_TEST_CALLBACK}#{test_id}')],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_share_test_link_to_classroom_keyboard(test_id: int, classrooms: list[Classroom]):
    classrooms_list = []
    for classroom in classrooms:
        classrooms_list.append(
            [get_button(classroom.title, f'{SPEC_SHARE_TEST_LINK_TO_CLASSROOM_CALLBACK}#{test_id}#{classroom.id}')])
    inline_keyboard = [
        *classrooms_list,
        [get_button(GO_TO_PREVIOUS_MENU_TEXT, f'{SPEC_CREATED_TEST_CALLBACK}#{test_id}')],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# CURRENT TESTS

def get_current_tests_menu_keyboard():
    inline_keyboard = [
        [get_button(CURRENT_ENDED_OR_WITH_NO_ATTEMPTS_TESTS_TEXT, CURRENT_ENDED_OR_WITH_NO_ATTEMPTS_TESTS_CALLBACK)],
        [get_button(CURRENT_AVAILABLE_TEST_WITH_ATTEMPTS_TEXT, CURRENT_AVAILABLE_TEST_WITH_ATTEMPTS_CALLBACK)],
        [BACK_TO_MAIN_MENU_BTN],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_current_tests_keyboard(tests: list[Test]):
    tests_list = []
    for test in tests:
        tests_list.append([get_button(test.title, f'{SPEC_CURRENT_TEST_CALLBACK}#{test.id}')])
    inline_keyboard = [
        *tests_list,
        [get_button(GO_TO_PREVIOUS_MENU_TEXT, CURRENT_TESTS_CALLBACK)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# RESPONDENT'S KEYBOARDS #

def get_respondent_buttons_():
    inline_keyboard = [
        [get_button(CURRENT_TESTS_TEXT, CURRENT_TESTS_CALLBACK)],
    ]
    return inline_keyboard


# COMMON KEYBOARDS #
def get_main_menu_keyboard():
    inline_keyboard = get_authors_buttons_() + get_respondent_buttons_()
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_back_to_main_menu_keyboard():
    inline_keyboard = [
        [BACK_TO_MAIN_MENU_BTN],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_go_to_main_menu_keyboard():
    inline_keyboard = [
        [GO_TO_MAIN_MENU_BTN],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
