from typing import Any, Optional

from aiogram.types import InlineKeyboardButton

from src.examobot.bot.Button import Button


GO_TO_MAIN_MENU_TEXT = 'Главное меню'
GO_TO_PREVIOUS_MENU_TEXT = 'Назад'
CANCEL_TEXT = 'Отмена'

BACK_TO_MAIN_MENU = Button(name='BACK_TO_MAIN_MENU', text='Главное меню')

### FOR AUTHORS ###

DELETE_ENTITY_CONFIRM = Button(name='DELETE_ENTITY_CONFIRM', text='Удалить')

# Classrooms

AUTHORS_CLASSROOMS = Button(name='AUTHORS_CLASSROOMS', text='Мои подборки')

SPEC_CREATED_CLASSROOM = Button(name='SPEC_CREATED_CLASSROOM', text='Выбрать подборку')

CREATE_CLASSROOM = Button(name='CREATE_CLASSROOM', text='Создать подборку')

DELETE_CLASSROOM = Button(name='DELETE_CLASSROOM', text='Удалить подборку')

SHOW_CLASSROOM_PARTICIPANTS = Button(name='SHOW_CLASSROOM_PARTICIPANTS', text='Показать участников')

EDIT_CLASSROOM = Button(name='EDIT_CLASSROOM', text='Изменить подборку')

EDIT_CLASSROOM_TITLE = Button(name='EDIT_CLASSROOM_TITLE', text='Изменить название подборки')

# created Tests

AUTHORS_TESTS = Button(name='AUTHORS_TESTS', text='Мои тесты')

SPEC_CREATED_TEST = Button(name='SPEC_CREATED_TEST', text='Выбрать тест')

CREATE_TEST = Button(name='CREATE_TEST', text='Создать тест')

SAVE_TEST = Button(name='SAVE_TEST', text='Сохранить тест')

SAVE_TEST_WITH_ADDITIONALS = Button(name='SAVE_TEST_WITH_ADDITIONALS', text='Добавить настройки')

CANCEL_ADDITION = Button(name='CANCEL_ADDITION', text='Пропустить')

CLOSE_TEST = Button(name='CLOSE_TEST', text='Закрыть тест')

OPEN_TEST = Button(name='OPEN_TEST', text='Открыть тест')

REFRESH_TEST_DATA = Button(name='REFRESH_TEST_DATA', text='Обновить данные теста')

DELETE_TEST = Button(name='DELETE_TEST', text='Удалить тест')

EDIT_TEST = Button(name='EDIT_TEST', text='Изменить тест')

EDIT_TEST_TITLE = Button(name='EDIT_TEST_TITLE', text='Изменить название теста')

EDIT_TEST_TIME = Button(name='EDIT_TEST_TIME', text='Изменить время')

EDIT_TEST_DEADLINE = Button(name='EDIT_TEST_DEADLINE', text='Изменить дедлайн')

EDIT_TEST_ATTEMPTS_NUMBER = Button(name='EDIT_TEST_ATTEMPTS_NUMBER', text='Изменить число попыток')

EDIT_TEST_LINK = Button(name='EDIT_TEST_LINK', text='Изменить ссылку Google Forms')

SHARE_TEST_LINK = Button(name='SHARE_TEST_LINK', text='Поделить ссылкой')

SHARE_TEST_LINK_TO_CLASSROOM = Button(name='SHARE_TEST_LINK_TO_CLASSROOM', text='Отправить тест участникам')

SPEC_SHARE_TEST_LINK_TO_CLASSROOM = Button(name='SPEC_SHARE_TEST_LINK_TO_CLASSROOM',
                                           text='specific share link to classroom')

### FOR PARTICIPANTS ###

CURRENT_CLASSROOMS = Button(name='CURRENT_CLASSROOMS', text='Доступные подборки')

SPEC_CURRENT_CLASSROOM = Button(name='SPEC_CURRENT_CLASSROOM', text='specific current classroom')

# current Classrooms

# current tests

CURRENT_TESTS = Button(name='CURRENT_TESTS', text='Доступные тесты')

SPEC_CURRENT_TEST = Button(name='SPEC_CURRENT_TEST', text='specific current test')

START_CURRENT_TEST = Button(name='START_CURRENT_TEST', text='Начать')

CURRENT_ENDED_OR_WITH_NO_ATTEMPTS_TESTS = Button(
    name='CURRENT_ENDED_OR_WITH_NO_ATTEMPTS_TESTS', text='Завершенные')

CURRENT_AVAILABLE_TEST_WITH_ATTEMPTS = Button(
    name='CURRENT_AVAILABLE_TEST_WITH_ATTEMPTS', text='Доступные опросы')

SPEC_CURRENT_TEST_TASK = Button(name='SPEC_CURRENT_TEST_TASK', text='question')

