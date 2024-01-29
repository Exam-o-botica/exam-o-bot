from aiogram import types

from keyboard_texts import *
from Entity import Entity
from src.examobot.db.tables import *

BACK_TO_MAIN_MENU_BUTTON = BACK_TO_MAIN_MENU.get_button()
GO_TO_MAIN_MENU_BUTTON = BACK_TO_MAIN_MENU.get_button(new_text=GO_TO_MAIN_MENU_TEXT)


def get_button_to_prev_menu(button: Button, parameters: list[Any], new_text: str = GO_TO_PREVIOUS_MENU_TEXT):
    return button.get_button(parameters=parameters, new_text=new_text)


# AUTHOR'S KEYBOARDS #

def get_authors_buttons_():
    inline_keyboard = [
        [AUTHORS_CLASSROOMS.get_button()],
        [AUTHORS_TESTS.get_button()],
    ]
    return inline_keyboard


def get_delete_entity_confirm_keyboard(entity: Entity, entity_id: int):
    inline_keyboard = [
        [DELETE_ENTITY_CONFIRM.get_button(parameters=[entity.name, entity_id])],
        [get_button_to_prev_menu(button=SPEC_CREATED_CLASSROOM, parameters=[entity_id], new_text='cancel')],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# CREATED CLASSROOMS

def get_classrooms_keyboard(classrooms: list[Classroom], classroom_type: str = 'created'):
    if classroom_type == 'created':
        btn = SPEC_CREATED_CLASSROOM
        create_classroom_btn = [CREATE_CLASSROOM.get_button()]
    elif classroom_type == 'current':
        btn = SPEC_CURRENT_CLASSROOM
        create_classroom_btn = []
    else:
        raise ValueError(f'Unknown classroom type: {classroom_type}, expected "created" or "current"')

    classrooms_list = [
        [btn.get_button(new_text=clm.title, parameters=[clm.id])] for clm in classrooms
    ]

    inline_keyboard = [
        *classrooms_list,
        create_classroom_btn,
        [BACK_TO_MAIN_MENU_BUTTON],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_spec_classroom_keyboard(classroom: Classroom):
    inline_keyboard = [
        [SHOW_CLASSROOM_PARTICIPANTS.get_button(parameters=[classroom.id])],
        [DELETE_CLASSROOM.get_button(parameters=[classroom.id])],
        [AUTHORS_CLASSROOMS.get_button(new_text=GO_TO_PREVIOUS_MENU_TEXT)],
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
        [CURRENT_CLASSROOMS.get_button()],
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


def go_to_previous_menu_keyboard(button: Button, parameters=None):
    if parameters is None:
        parameters = []
    inline_keyboard = [
        [button.get_button(parameters=parameters, new_text=GO_TO_PREVIOUS_MENU_TEXT)],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
