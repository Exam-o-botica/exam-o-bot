from aiogram.types import InlineKeyboardMarkup

from src.examobot.db.tables import Task
from src.examobot.task_translator.keyboard_task_texts import *
from aiogram import types


def make_pinned_option_text(order_number: int, chosen_options: list[int]) -> str:
    chosen_options_set = set(chosen_options)
    text = f"вариант {order_number}"
    if order_number in chosen_options_set:
        text = text + " 📌"

    return text


def get_no_options_keyboard(task: Task):
    inline_keyboard = [
        [BACK_TO_TEST_QUESTION_FROM_TASK.get_button(parameters=[task.test_id])]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_one_choice_keyboard(task: Task, options_num: int, chosen_answer: int | None = None):
    choices = [
        [
            ONE_CHOICE_QUESTION_OPTION.get_button(
                new_text=f"вариант {i}{' 📌' if i == chosen_answer else ''}",
                parameters=[task.id, i])
        ]
        for i in range(1, options_num + 1)
    ]
    inline_keyboard = [
        # [
        #     ONE_CHOICE_QUESTION_OPTION.get_button(
        #         new_text=f"вариант {i}{' 📌' if i == chosen_answer else ''}",
        #         parameters=[task.id, i])
        #     for i in range(1, options_num + 1)
        # ],
        *choices,
        [BACK_TO_TEST_QUESTION_FROM_TASK.get_button(parameters=[task.test_id])]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_multiple_choice_keyboard(task: Task, options_num: int, chosen_options: list[int]):
    inline_keyboard = [
        [
            MULTIPLE_CHOICE_QUESTION_OPTION.get_button(
                new_text=make_pinned_option_text(i, chosen_options), parameters=[task.id, i])
            for i in range(1, options_num + 1)
        ],
        [BACK_TO_TEST_QUESTION_FROM_TASK.get_button(parameters=[task.test_id])]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
