from typing import Any, Optional

from aiogram.types import InlineKeyboardButton


class Button:
    callback_suffix: str = "_callback"

    def __init__(self, name: str, text: str) -> None:
        self.name = name
        self.txt = text

    @property
    def text(self):
        return self.txt

    @property
    def callback(self):
        return self.name.lower() + self.callback_suffix

    def get_button(self,
                   new_text: Optional[str] = None,
                   parameters: Optional[list[Any]] = None,
                   ) -> InlineKeyboardButton:
        callback = self.callback
        if parameters:
            callback = callback + "#" + "#".join([str(p) for p in parameters])

        text = new_text if new_text else self.txt
        return InlineKeyboardButton(text=text, callback_data=callback)

    def has_that_callback(self, received_callback: str):
        return received_callback.startswith(self.callback)


GO_TO_MAIN_MENU_TEXT = 'go to menu'
GO_TO_PREVIOUS_MENU_TEXT = 'Back'
CANCEL_TEXT = 'cancel'

BACK_TO_MAIN_MENU = Button(name='BACK_TO_MAIN_MENU', text='back to main menu')

### FOR AUTHORS ###

DELETE_ENTITY_CONFIRM = Button(name='DELETE_ENTITY_CONFIRM', text='delete')

# Classrooms

AUTHORS_CLASSROOMS = Button(name='AUTHORS_CLASSROOMS', text='created classrooms')

SPEC_CREATED_CLASSROOM = Button(name='SPEC_CREATED_CLASSROOM', text='specific classroom')

CREATE_CLASSROOM = Button(name='CREATE_CLASSROOM', text='add classroom')

DELETE_CLASSROOM = Button(name='DELETE_CLASSROOM', text='delete classroom')

SHOW_CLASSROOM_PARTICIPANTS = Button(name='SHOW_CLASSROOM_PARTICIPANTS', text='show participants')

EDIT_CLASSROOM = Button(name='EDIT_CLASSROOM', text='edit classroom')

EDIT_CLASSROOM_TITLE = Button(name='EDIT_CLASSROOM_TITLE', text='edit title')

# created Tests

AUTHORS_TESTS = Button(name='AUTHORS_TESTS', text='created tests')

SPEC_CREATED_TEST = Button(name='SPEC_CREATED_TEST', text='specific test')

CREATE_TEST = Button(name='CREATE_TEST', text='add test')

SAVE_TEST = Button(name='SAVE_TEST', text='save test')

SAVE_TEST_WITH_ADDITIONALS = Button(name='SAVE_TEST_WITH_ADDITIONALS', text='add more')

CANCEL_ADDITION = Button(name='CANCEL_ADDITION', text='skip')

CLOSE_TEST = Button(name='CLOSE_TEST', text='close test')

OPEN_TEST = Button(name='OPEN_TEST', text='open test')

REFRESH_TEST_DATA = Button(name='REFRESH_TEST_DATA', text='refresh test data')

DELETE_TEST = Button(name='DELETE_TEST', text='delete test')

EDIT_TEST = Button(name='EDIT_TEST', text='edit test')

EDIT_TEST_TITLE = Button(name='EDIT_TEST_TITLE', text='edit title')

EDIT_TEST_TIME = Button(name='EDIT_TEST_TIME', text='edit duration')

EDIT_TEST_DEADLINE = Button(name='EDIT_TEST_DEADLINE', text='edit deadline')

EDIT_TEST_ATTEMPTS_NUMBER = Button(name='EDIT_TEST_ATTEMPTS_NUMBER', text='edit number of attempts')

EDIT_TEST_LINK = Button(name='EDIT_TEST_LINK', text='edit link to form')

SHARE_TEST_LINK = Button(name='SHARE_TEST_LINK', text='share test link')

SHARE_TEST_LINK_TO_CLASSROOM = Button(name='SHARE_TEST_LINK_TO_CLASSROOM', text='send test to classroom')

SPEC_SHARE_TEST_LINK_TO_CLASSROOM = Button(name='SPEC_SHARE_TEST_LINK_TO_CLASSROOM',
                                           text='specific share link to classroom')

### FOR PARTICIPANTS ###

CURRENT_CLASSROOMS = Button(name='CURRENT_CLASSROOMS', text='current classrooms')

SPEC_CURRENT_CLASSROOM = Button(name='SPEC_CURRENT_CLASSROOM', text='specific current classroom')

# current Classrooms

# current tests

CURRENT_TESTS = Button(name='CURRENT_TESTS', text='current tests')

SPEC_CURRENT_TEST = Button(name='SPEC_CURRENT_TEST', text='specific current test')

START_CURRENT_TEST = Button(name='START_CURRENT_TEST', text='start test')

CURRENT_ENDED_OR_WITH_NO_ATTEMPTS_TESTS = Button(
    name='CURRENT_ENDED_OR_WITH_NO_ATTEMPTS_TESTS', text='ended tests')

CURRENT_AVAILABLE_TEST_WITH_ATTEMPTS = Button(
    name='CURRENT_AVAILABLE_TEST_WITH_ATTEMPTS', text='available tests')
