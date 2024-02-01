from aiogram.types import InlineKeyboardMarkup

from examobot.task_translator.keyboard_task_texts import *
from aiogram import types


def make_pinned_option_text(order_number: int, chosen_options: list[int]) -> str:
    chosen_options_set = set(chosen_options)
    text = f"вариант {order_number}"
    if order_number in chosen_options_set:
        text = text + " 📌"

    return text


def get_one_choice_keyboard(task_id: int, options_num: int, chosen_answer: int | None = None):
    inline_keyboard = [
        [ONE_CHOICE_QUESTION_OPTION.get_button(new_text=f"вариант {i}{' 📌' if i == chosen_answer else ''}", parameters=[task_id, i]) for i in
         range(1, options_num + 1)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_multiple_choice_keyboard(task_id: int, options_num: int, chosen_options: list[int]):
    inline_keyboard = [
        [
            MULTIPLE_CHOICE_QUESTION_OPTION.get_button(
                new_text=make_pinned_option_text(i, chosen_options), parameters=[task_id, i])
            for i in range(1, options_num + 1)
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
