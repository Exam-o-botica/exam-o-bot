from aiogram import Router, Bot
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery

from src.examobot.bot.keyboards import get_go_to_main_menu_keyboard, get_current_test_tasks_keyboard
from src.examobot.db.manager import db_manager
from src.examobot.db.tables import Task, Test
from src.examobot.task_translator.QuestionType import QuestionType
from src.examobot.task_translator.questions_classes import Question, OneChoiceQuestion, MultipleChoiceQuestion

tasks_router = Router(name="tasks_router")


async def delete_question_messages(bot: Bot, user_id: int):
    user = await db_manager.get_user_by_id(user_id)
    if user.current_messages_to_delete:
        for message_id in user.current_messages_to_delete:
            try:
                await bot.delete_message(user_id, message_id)
            except Exception:
                pass

        await db_manager.update_user_by_id(user_id, current_messages_to_delete=[])


async def get_task_safe(
        task_id: int,
        chat_id: int,
        bot: Bot, message_id: int,
        error_reply_markup: InlineKeyboardMarkup = None
) -> Task | None:
    task = await db_manager.get_task_by_id(task_id)
    if not task:
        await bot.edit_message_text(
            text="Тест был удален",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=error_reply_markup
        )

    return task


async def get_test_safe(
        test_id: int, chat_id: int, bot: Bot, message_id: int,
        error_reply_markup: InlineKeyboardMarkup = None) -> Test | None:
    test = await db_manager.get_test_by_id(test_id)
    if not test:
        await bot.edit_message_text(
            text="this test was deleted by author",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=error_reply_markup
        )

    return test


async def show_menu_with_tasks(cur_test_id: int, bot: Bot, chat_id: int, test_title: str):
    tasks: list[Task] = await db_manager.get_tasks_by_test_id(cur_test_id)
    await bot.send_message(
        chat_id,
        test_title,
        reply_markup=get_current_test_tasks_keyboard(tasks)
    )


async def get_current_user_test_task_state(user_id: int, bot: Bot, message_id: int):
    user = await db_manager.get_user_by_id(user_id)
    if not user:
        return None, None, None

    cur_test_id = user.current_test_id
    cur_task_id = user.current_task_id
    if not cur_test_id or not cur_task_id:
        await bot.delete_message(user_id, message_id)
        return user, None, None

    return user, cur_test_id, cur_task_id


async def handle_question(
        question: Question,
        message_or_call: Message | CallbackQuery,
        user_id: int, bot: Bot,
        message_id: int,
        task: Task = None
):
    user, cur_test_id, cur_task_id = await get_current_user_test_task_state(
        user_id=user_id,
        bot=bot,
        message_id=message_id
    )
    if not cur_test_id or not cur_task_id:
        return

    if not task:
        task_id = cur_task_id
        task = await get_task_safe(
            task_id=task_id,
            chat_id=user_id,
            bot=bot,
            message_id=message_id,
            error_reply_markup=get_go_to_main_menu_keyboard()
        )
        if not task:
            return

    task_id = task.id

    await delete_question_messages(bot=bot, user_id=user_id)
    await question.save_answer(message_or_call, task_id)
    await db_manager.update_user_by_id(user_id, current_task_id=None)

    test = await get_test_safe(
        test_id=cur_test_id,
        chat_id=user_id,
        bot=bot,
        message_id=message_id,
        error_reply_markup=get_go_to_main_menu_keyboard()
    )
    if not test:
        return

    await bot.send_message(text="Ответ сохранён", chat_id=user_id)
    await show_menu_with_tasks(
        cur_test_id=cur_test_id,
        bot=bot,
        chat_id=user_id,
        test_title=test.title
    )


async def handle_question_with_call(question: Question, call: CallbackQuery):
    user_id = call.from_user.id
    bot = call.bot
    message_id = call.message.message_id

    await handle_question(
        question=question,
        message_or_call=call,
        user_id=user_id,
        bot=bot,
        message_id=message_id
    )


@tasks_router.message()
async def handle_message_sent_by_user(message: Message):
    user_id = message.from_user.id
    bot = message.bot
    message_id = message.message_id

    user, cur_test_id, cur_task_id = await get_current_user_test_task_state(
        user_id=user_id,
        bot=bot,
        message_id=message_id
    )
    if not cur_test_id or not cur_task_id:
        return

    task = await db_manager.get_task_by_id(cur_task_id)
    task_type = task.task_type

    type_names_to_handle = QuestionType.get_names_of_types_with_message_answers()
    if task_type not in type_names_to_handle:
        await bot.delete_message(user_id, message_id)
        return

    question: Question = QuestionType[task_type].value
    if not question.is_valid_answer(message):
        await message.answer("invalid format of answer. please, try again")
        await bot.delete_message(user_id, message_id)

    await handle_question(
        question=question,
        message_or_call=message,
        user_id=user_id,
        bot=bot,
        message_id=message_id,
        task=task
    )


async def handle_one_choice_question_option_query(call: CallbackQuery):
    await handle_question_with_call(OneChoiceQuestion(), call)


async def handle_multiple_choice_question_option_query(call: CallbackQuery):
    await handle_question_with_call(MultipleChoiceQuestion(), call)
