from typing import Any, Optional

from aiogram.types import InlineKeyboardButton

from examobot.bot.Button import Button

GO_TO_MAIN_MENU_TEXT = 'Главное меню'
GO_TO_PREVIOUS_MENU_TEXT = 'Назад'
CANCEL_TEXT = 'Отмена'

BACK_TO_MAIN_MENU = Button(name='BACK_TO_MAIN_MENU', text='Главное меню')

### FOR AUTHORS ###

DELETE_ENTITY_CONFIRM = Button(name='DELETE_ENTITY_CONFIRM', text='Удалить')

# Classrooms

AUTHORS_CLASSROOMS = Button(name='AUTHORS_CLASSROOMS', text='Мои группы')

SPEC_CREATED_CLASSROOM = Button(name='SPEC_CREATED_CLASSROOM', text='Выбрать группу')

CREATE_CLASSROOM = Button(name='CREATE_CLASSROOM', text='Создать группу')

DELETE_CLASSROOM = Button(name='DELETE_CLASSROOM', text='Удалить группу')

SHOW_CLASSROOM_PARTICIPANTS = Button(name='SHOW_CLASSROOM_PARTICIPANTS', text='Показать участников')

EDIT_CLASSROOM = Button(name='EDIT_CLASSROOM', text='Изменить группу')

EDIT_CLASSROOM_TITLE = Button(name='EDIT_CLASSROOM_TITLE', text='Изменить название группы')

# created Tests

AUTHORS_TESTS = Button(name='AUTHORS_TESTS', text='Мои опросы')

SPEC_CREATED_TEST = Button(name='SPEC_CREATED_TEST', text='Выбрать опрос')

CREATE_TEST = Button(name='CREATE_TEST', text='Создать опрос')

SAVE_TEST = Button(name='SAVE_TEST', text='Сохранить опрос')

SAVE_TEST_WITH_ADDITIONALS = Button(name='SAVE_TEST_WITH_ADDITIONALS', text='Добавить настройки')

CANCEL_ADDITION = Button(name='CANCEL_ADDITION', text='Пропустить')

CLOSE_TEST = Button(name='CLOSE_TEST', text='Закрыть опрос')

OPEN_TEST = Button(name='OPEN_TEST', text='Открыть опрос')

REFRESH_TEST_DATA = Button(name='REFRESH_TEST_DATA', text='Обновить данные опроса')

DELETE_TEST = Button(name='DELETE_TEST', text='Удалить опрос')

EDIT_TEST = Button(name='EDIT_TEST', text='Изменить опрос')

EDIT_TEST_TITLE = Button(name='EDIT_TEST_TITLE', text='Изменить название опроса')

EDIT_TEST_TIME = Button(name='EDIT_TEST_TIME', text='Изменить время')

EDIT_TEST_DEADLINE = Button(name='EDIT_TEST_DEADLINE', text='Изменить дедлайн')

EDIT_TEST_ATTEMPTS_NUMBER = Button(name='EDIT_TEST_ATTEMPTS_NUMBER', text='Изменить число попыток')

EDIT_TEST_LINK = Button(name='EDIT_TEST_LINK', text='Изменить ссылку Google Forms')

SHARE_TEST_LINK = Button(name='SHARE_TEST_LINK', text='Поделить ссылкой')

SHARE_TEST_LINK_TO_CLASSROOM = Button(name='SHARE_TEST_LINK_TO_CLASSROOM', text='Отправить опрос участникам')

SPEC_SHARE_TEST_LINK_TO_CLASSROOM = Button(name='SPEC_SHARE_TEST_LINK_TO_CLASSROOM',
                                           text='Выбранная ссылка на группу')

### FOR PARTICIPANTS ###

CURRENT_CLASSROOMS = Button(name='CURRENT_CLASSROOMS', text='Доступные группы')

SPEC_CURRENT_CLASSROOM = Button(name='SPEC_CURRENT_CLASSROOM', text='Выбранная группа')

# current Classrooms

# current tests

CURRENT_TESTS = Button(name='CURRENT_TESTS', text='Доступные опросы')

SPEC_CURRENT_TEST = Button(name='SPEC_CURRENT_TEST', text='Выбранный опрос')

START_CURRENT_TEST = Button(name='START_CURRENT_TEST', text='Начать')

CURRENT_ENDED_OR_WITH_NO_ATTEMPTS_TESTS = Button(
    name='CURRENT_ENDED_OR_WITH_NO_ATTEMPTS_TESTS', text='Завершенные')

CURRENT_AVAILABLE_TEST_WITH_ATTEMPTS = Button(
    name='CURRENT_AVAILABLE_TEST_WITH_ATTEMPTS', text='Доступные')

SPEC_CURRENT_TEST_TASK = Button(name='SPEC_CURRENT_TEST_TASK', text='Вопрос')
