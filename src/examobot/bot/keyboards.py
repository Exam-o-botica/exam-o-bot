from aiogram import types

from keyboard_texts import *
from src.examobot.db.tables import *

BACK_TO_MAIN_MENU_BUTTON = BACK_TO_MAIN_MENU.get_button()
GO_TO_MAIN_MENU_BUTTON = BACK_TO_MAIN_MENU.get_button(new_text=GO_TO_MAIN_MENU_TEXT)


# AUTHOR'S KEYBOARDS #

def get_authors_buttons_():
    inline_keyboard = [
        [AUTHORS_CLASSROOMS.get_button()],
        [AUTHORS_TESTS.get_button()],
    ]
    return inline_keyboard


# CREATED CLASSROOMS

def get_created_classrooms_keyboard(classrooms: list[Classroom]):
    classrooms_list = [
        [SPEC_CREATED_CLASSROOM.get_button(new_text=clm.title, parameters=[clm.id])] for clm in classrooms
    ]

    inline_keyboard = [
        *classrooms_list,
        [CREATE_CLASSROOM.get_button()],
        [BACK_TO_MAIN_MENU_BUTTON],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_spec_classroom_keyboard(classroom: Classroom):
    inline_keyboard = [
        [get_button(DELETE_CLASSROOM_TEXT, f"{DELETE_CLASSROOM_CALLBACK}#{classroom.id}")],
        [get_button(GO_TO_PREVIOUS_MENU_TEXT, AUTHORS_CLASSROOMS_CALLBACK)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_emoji_test_status(status: TestStatus):
    if status == TestStatus.AVAILABLE:
        return '🟢'
    else:
        return '🔴'


def get_created_tests_keyboard(tests: list[Test]):
    tests_list = [
        [
            SPEC_CREATED_TEST.get_button(
                new_text=str(f"{t.title} {get_emoji_test_status(t.status_set_by_author)}"),
                parameters=[t.id]
            )
        ]
        for t in tests
    ]

    inline_keyboard = [
        *tests_list,
        [CREATE_TEST.get_button()],
        [BACK_TO_MAIN_MENU_BUTTON],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_spec_created_test_keyboard(test: Test):
    inline_keyboard = [
        [CLOSE_TEST.get_button(parameters=[test.id])],
        [REFRESH_TEST_DATA.get_button(parameters=[test.id])],
        [EDIT_TEST.get_button(parameters=[test.id])],
        [SHARE_TEST_LINK.get_button(parameters=[test.id])],
        [AUTHORS_TESTS.get_button(new_text=GO_TO_PREVIOUS_MENU_TEXT)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_share_test_link_keyboard(test_id: int):
    inline_keyboard = [
        [SHARE_TEST_LINK_TO_CLASSROOM.get_button(parameters=[test_id])],
        [SPEC_CREATED_TEST.get_button(new_text=GO_TO_PREVIOUS_MENU_TEXT, parameters=[test_id])],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_share_test_link_to_classroom_keyboard(test_id: int, classrooms: list[Classroom]):
    classrooms_list = [
        [SPEC_SHARE_TEST_LINK_TO_CLASSROOM.get_button(new_text=clm.title, parameters=[test_id, clm.id])]
        for clm in classrooms
    ]

    inline_keyboard = [
        *classrooms_list,
        [SPEC_CREATED_TEST.get_button(new_text=GO_TO_PREVIOUS_MENU_TEXT, parameters=[test_id])],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# CURRENT TESTS

def get_current_tests_menu_keyboard():
    inline_keyboard = [
        [CURRENT_ENDED_OR_WITH_NO_ATTEMPTS_TESTS.get_button()],
        [CURRENT_AVAILABLE_TEST_WITH_ATTEMPTS.get_button()],
        [BACK_TO_MAIN_MENU_BUTTON],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_current_tests_keyboard(tests: list[Test]):
    tests_list = [
        [SPEC_CURRENT_TEST.get_button(new_text=t.title, parameters=[t.id]) for t in tests]
    ]

    inline_keyboard = [
        *tests_list,
        [CURRENT_TESTS.get_button(new_text=GO_TO_PREVIOUS_MENU_TEXT)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# RESPONDENT'S KEYBOARDS #

def get_respondent_buttons_():
    inline_keyboard = [
        [CURRENT_TESTS.get_button()],
    ]
    return inline_keyboard


# COMMON KEYBOARDS #
def get_main_menu_keyboard():
    inline_keyboard = get_authors_buttons_() + get_respondent_buttons_()
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_back_to_main_menu_keyboard():
    inline_keyboard = [
        [BACK_TO_MAIN_MENU_BUTTON],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_go_to_main_menu_keyboard():
    inline_keyboard = [
        [GO_TO_MAIN_MENU_BUTTON],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
