from src.examobot.task_translator.keyboard_task_texts import ONE_CHOICE_QUESTION_OPTION
from aiogram import types


def get_one_choice_keyboard(task_id: int, options_num: int, chosen_answer: int | None = None):
    inline_keyboard = [
        [ONE_CHOICE_QUESTION_OPTION.get_button(new_text=f"вариант {i}{' 📌' if i == chosen_answer else ''}", parameters=[task_id, i]) for i in
         range(1, options_num + 1)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
