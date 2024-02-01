def get_task_options_keyboard(task_id: int, options_num: int):
    inline_keyboard = [
        [ONE_CHOICE_QUESTION_OPTION.get_button(new_text=f"вариант {i}", parameters=[task_id]) for i in
         range(1, options_num + 1)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)