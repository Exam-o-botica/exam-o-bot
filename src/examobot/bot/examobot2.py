import asyncio
import json
import logging
import os
import re
import sys
import time
import types
from datetime import datetime
from pprint import pprint

from aiogram import Dispatcher, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from consts import *
from keyboards import *
# from src.examobot.db.manager import db_manager
from src.examobot.task_translator.QuestionType import QuestionType
# from src.examobot.task_translator.QuestionType import QuestionType

from src.examobot.task_translator.questions_classes import *
from src.examobot.task_translator.task_translator import Translator, TranslationError
from src.examobot.form_handlers import *
from src.examobot.db.tables import *
from src.examobot.bot.entity import Entity

# from src.main import bot, dp

TOKEN = os.getenv("EXAM_O_BOT_TOKEN")
dp = Dispatcher()


# db_manager = DBManager()


class Form(StatesGroup):
    edit_test_title = State()
    edit_test_time = State()
    edit_test_deadline = State()
    edit_test_attempts_number = State()
    edit_test_link = State()

    create_test_title = State()
    create_test_time = State()
    create_test_deadline = State()
    create_test_attempts_number = State()
    create_test_link = State()
    create_test_save = State()
    create_test_save_with_additions = State()

    edit_classroom_title = State()
    create_classroom_title = State()


'''
possible start links: 
    1. https://t.me/beermovent_bot?start=test={test_id}
    2. https://t.me/beermovent_bot?start=class={classroom_id}
    
    ex1: https://t.me/beermovent_bot?start=class=5069ut54303
    ex2: https://t.me/beermovent_bot?start=test=50et3695
'''

CREATION_FORMS = {
    "create_test_title": {
        "form": Form.create_test_title,
        "state_text": "type test title #",
        "next_state": "create_test_time",
    },
    "create_test_time": {
        "form": Form.create_test_time,
        "state_text": "type test time #",
        "next_state": "create_test_deadline",
    },
    "create_test_deadline": {
        "form": Form.create_test_deadline,
        "state_text": "type test deadline #",
        "next_state": "create_test_attempts_number",
    },
    "create_test_attempts_number": {
        "form": Form.create_test_attempts_number,
        "state_text": "type test attempts number #",
        "next_state": "create_test_save_with_additions",
    },
}

'''
possible start links: 
    1. https://t.me/beermovent_bot?start=test={test_id}
    2. https://t.me/beermovent_bot?start=class={classroom_id}
    
    ex1: https://t.me/beermovent_bot?start=class=5069ut54303
    ex2: https://t.me/beermovent_bot?start=test=50et3695
'''


class ValidationPatterns:
    TITLE = re.compile(r"(\w|\d)+(\s+(\w|\d)+)*")
    TIME = re.compile(r"\d+")
    DEADLINE = re.compile(r"\d\d\.\d\d\.\d\d\d\d\s\d\d:\d\d")
    ATTEMPTS_NUMBER = re.compile(r"\d+")
    LINK = re.compile(r"(http(s)?://)?docs\.google\.com/forms/d/[_a-zA-Z\d-]+/edit")

    @staticmethod
    def SHARE_LINK():
        return re.compile(
            r'[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}', re.I)


class Validations:
    @staticmethod
    def is_valid_share_link(link: str, link_type: str) -> bool:
        if link.startswith(link_type):
            link = link.removeprefix(link_type + '=')
        match = re.match(ValidationPatterns.SHARE_LINK(), link.strip())
        return match is not None

    @staticmethod
    async def validate_test_title(message: Message, text: str):
        if not re.fullmatch(ValidationPatterns.TITLE, text.strip()):
            await message.answer(text="title may contain letters, digits and spaces. please, rewrite")
            return None

        return text.strip()

    @staticmethod
    async def validate_test_time(message: Message, text: str):
        if not re.fullmatch(ValidationPatterns.TIME, text.strip()):
            await message.answer(text="duration may contain only digits. please, rewrite")
            return None

        return text.strip()

    @staticmethod
    async def validate_test_deadline(message: Message, text: str):
        if not re.fullmatch(ValidationPatterns.DEADLINE, text.strip()):
            await message.answer(text="please, follow the format: 'DD.MM.YYYY hh:mm'")
            return

        try:
            timestamp = int(
                time.mktime(
                    datetime.strptime(text.strip(), "%d.%m.%Y %H:%M").timetuple()))
        except Exception as e:
            pprint(f"Deadline error: {e}")
            await message.answer(text="seems like there is some error with the date. please, retry")
            return None

        return timestamp

    @staticmethod
    async def validate_test_attempts_number(message: Message, text: str):
        if not re.fullmatch(ValidationPatterns.ATTEMPTS_NUMBER, text.strip()):
            await message.answer(text="number of attempts may contain only digits. please, rewrite")
            return None

        return text.strip()


@dp.message(CommandStart())
async def welcome_message(message: types.Message, command: CommandObject) -> None:
    name = get_user_name(message.from_user)
    exists = await db_manager.check_if_user_exists(user_id=message.from_user.id)
    args = command.args

    if not exists:
        await db_manager.add_user(message.from_user.id, message.from_user.username, name=name)
        await message.bot.send_message(message.from_user.id, START_TEXT)

    await db_manager.update_user_by_id(
        message.from_user.id,
        current_task_id=None,
        current_test_id=None,
    )

    if not args:
        await message.bot.send_message(
            message.from_user.id,
            MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard())

    else:
        if Validations.is_valid_share_link(args, "class"):
            classroom_uuid = args.split("=")[1]
            classroom = await db_manager.get_classroom_by_uuid(classroom_uuid)
            if not classroom:
                await message.bot.send_message(
                    message.from_user.id,
                    text="this classroom doesn't exist",
                    reply_markup=get_go_to_main_menu_keyboard())

                return

            if await db_manager.check_if_user_in_classroom(classroom.id, message.from_user.id):
                # todo maybe we wanna consider that user is not author of this classroom
                await message.bot.send_message(
                    message.from_user.id,
                    text="you are already joined this classroom",
                    reply_markup=get_go_to_main_menu_keyboard())

                return

            await db_manager.add_user_to_classroom(classroom.id, message.from_user.id)
            await message.bot.send_message(
                message.from_user.id,
                SUCCESSFULLY_ADDED_TO_CLASSROOM.format(classroom.title),
                reply_markup=get_go_to_main_menu_keyboard())

            await send_message_to_user(
                message.bot,
                classroom.author_id,
                message=f"user @{message.from_user.username} joined your classroom \"{classroom.title}\"")

        elif Validations.is_valid_share_link(args, "test"):
            test_uuid = args.split("=")[1]
            test = await db_manager.get_test_by_uuid(test_uuid)
            if not test:
                await message.bot.send_message(
                    message.from_user.id,
                    text="link is invalid, test doesn't exist",
                    reply_markup=get_go_to_main_menu_keyboard())

                return

            if await db_manager.check_if_user_in_test(test.id, message.from_user.id):
                # todo maybe we wanna consider that user is not author of this test
                await message.bot.send_message(
                    message.from_user.id,
                    text="you are already able to pass this test",
                    reply_markup=get_go_to_main_menu_keyboard())

                return

            await db_manager.add_user_to_test_participants(test.id, message.from_user.id)
            await message.bot.send_message(
                message.from_user.id,
                SUCCESSFULLY_ADDED_TO_TESTS.format(test.title),
                reply_markup=get_go_to_main_menu_keyboard())

        else:
            await message.bot.send_message(
                message.from_user.id,
                text="link is invalid",
                reply_markup=get_go_to_main_menu_keyboard())


def get_user_name(user: types.User) -> str:
    name = ""
    if user.first_name:
        name += user.first_name
    if user.last_name:
        name += f" {user.last_name}"
    return name


async def send_message_to_user(bot: Bot, user_id: int, message: str, reply_markup=None) -> None:
    try:
        await bot.send_message(user_id, message, reply_markup=reply_markup)
    except Exception as e:
        logging.error(f"error while sending message to user {user_id}: {e}")


@dp.callback_query()
async def callback_inline(call: types.CallbackQuery, state: FSMContext) -> None:
    # main menu authors options

    if BACK_TO_MAIN_MENU.has_that_callback(call.data):
        await call.bot.edit_message_text(MAIN_MENU_TEXT, call.from_user.id, call.message.message_id,
                                         reply_markup=get_main_menu_keyboard())

    # CREATED CLASSROOMS

    elif AUTHORS_CLASSROOMS.has_that_callback(call.data):
        await handle_authors_classrooms_query(call)

    elif CREATE_CLASSROOM.has_that_callback(call.data):
        await handle_create_classroom_query(call, state)

    elif EDIT_CLASSROOM.has_that_callback(call.data):
        await handle_edit_classroom_query(call)

    elif EDIT_CLASSROOM_TITLE.has_that_callback(call.data):
        await handle_edit_classroom_title_query(call, state)

    # CREATED TESTS

    elif CREATE_TEST.has_that_callback(call.data):
        await handle_create_test_query(call, state)

    elif SAVE_TEST.has_that_callback(call.data):
        await handle_save_test_query(call, state)

    elif SAVE_TEST_WITH_ADDITIONALS.has_that_callback(call.data):
        await handle_save_test_with_additionals_query(call, state)

    elif CANCEL_ADDITION.has_that_callback(call.data):
        await handle_cancel_addition_query(call, state)

    elif EDIT_TEST.has_that_callback(call.data):
        await handle_edit_test_query(call, state)

    elif EDIT_TEST_TITLE.has_that_callback(call.data):
        await handle_edit_test_title_query(call, state)

    elif EDIT_TEST_TIME.has_that_callback(call.data):
        await handle_edit_test_time_query(call, state)

    elif EDIT_TEST_DEADLINE.has_that_callback(call.data):
        await handle_edit_test_deadline_query(call, state)

    elif EDIT_TEST_ATTEMPTS_NUMBER.has_that_callback(call.data):
        await handle_edit_test_attempts_number_query(call, state)

    elif EDIT_TEST_LINK.has_that_callback(call.data):
        await handle_edit_test_link_query(call, state)

    elif AUTHORS_TESTS.has_that_callback(call.data):
        await handle_authors_tests_query(call, state)

    elif SPEC_CREATED_TEST.has_that_callback(call.data):
        await handle_spec_created_test_query(call, state)

    elif SHARE_TEST_LINK.has_that_callback(call.data):
        await handle_share_test_link_query(call)

    elif SHARE_TEST_LINK_TO_CLASSROOM.has_that_callback(call.data):
        await handle_share_test_link_to_classroom_query(call)

    elif SPEC_SHARE_TEST_LINK_TO_CLASSROOM.has_that_callback(call.data):
        await handle_spec_share_test_link_to_classroom_query(call)

    elif SPEC_CREATED_CLASSROOM.has_that_callback(call.data):
        await handle_spec_created_classroom_query(call)

    elif SHOW_CLASSROOM_PARTICIPANTS.has_that_callback(call.data):
        await handle_show_classroom_participants_query(call)

    elif DELETE_CLASSROOM.has_that_callback(call.data):
        await handle_delete_classroom_query(call)

    elif DELETE_ENTITY_CONFIRM.has_that_callback(call.data):
        await handle_delete_entity_confirm_query(call)

    elif CLOSE_TEST.has_that_callback(call.data):
        await handle_change_test_status_query(call, TestStatus.UNAVAILABLE)

    elif OPEN_TEST.has_that_callback(call.data):
        await handle_change_test_status_query(call, TestStatus.AVAILABLE)

    elif REFRESH_TEST_DATA.has_that_callback(call.data):
        await handle_refresh_test_data_query(call)

    elif DELETE_TEST.has_that_callback(call.data):
        await handle_delete_test_query(call)

    # CURRENT TESTS

    elif CURRENT_TESTS.has_that_callback(call.data):
        await call.bot.edit_message_text(
            "choose test types",
            call.from_user.id,
            call.message.message_id,
            reply_markup=get_current_tests_menu_keyboard())

    elif CURRENT_AVAILABLE_TEST_WITH_ATTEMPTS.has_that_callback(call.data):
        await handle_current_available_test_with_attempts_query(call)

    elif CURRENT_ENDED_OR_WITH_NO_ATTEMPTS_TESTS.has_that_callback(call.data):
        await handle_current_ended_or_with_no_attempts_tests_query(call)

    elif SPEC_CURRENT_TEST.has_that_callback(call.data):
        await handle_spec_current_test_query(call)

    elif START_CURRENT_TEST.has_that_callback(call.data):
        await handle_start_current_test_query(call)

    elif SPEC_CURRENT_TEST_TASK.has_that_callback(call.data):
        await handle_spec_current_test_task_query(call)

    elif BACK_TO_TEST_QUESTION_FROM_TASK.has_that_callback(call.data):
        await handle_back_to_test_question_from_task_query(call)

    # elif END_TEST.has_that_callback(call.data):
    #     await handle_end_test_query(call)

    # QUESTIONS

    # elif ONE_CHOICE_QUESTION_OPTION.has_that_callback(call.data):
    #     await handle_one_choice_question_option_query(call)

    # elif MULTIPLE_CHOICE_QUESTION_OPTION.has_that_callback(call.data):
    #     await handle_multiple_choice_question_option_query(call)

    # CURRENT CLASSROOMS

    elif CURRENT_CLASSROOMS.has_that_callback(call.data):
        await handle_current_classrooms_query(call)

    elif SPEC_CURRENT_CLASSROOM.has_that_callback(call.data):
        await handle_spec_current_classroom_query(call)


async def handle_back_to_test_question_from_task_query(call: types.CallbackQuery):
    await db_manager.update_user_by_id(call.from_user.id, current_task_id=None)
    test_id = get_test_id_or_classroom_id_from_callback(call.data)
    test = await db_manager.get_test_by_id(test_id)
    if not test:
        await call.bot.edit_message_text(
            "this test was deleted by author",
            call.from_user.id,
            call.message.message_id,
            reply_markup=get_go_to_main_menu_keyboard()
        )
        return

    tasks: list[Task] = await db_manager.get_tasks_by_test_id(test_id)
    await call.bot.edit_message_text(
        test.title,
        call.from_user.id,
        call.message.message_id,
        reply_markup=get_current_test_tasks_keyboard(tasks)
    )


async def handle_spec_current_test_task_query(call: types.CallbackQuery):
    task_id = get_test_id_or_classroom_id_from_callback(call.data)
    task = await db_manager.get_task_by_id(task_id)
    if not task:
        await call.bot.edit_message_text(
            text="this test was deleted by author",
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=get_go_to_main_menu_keyboard()
        )
        return

    await call.bot.delete_message(call.from_user.id, call.message.message_id)

    question = QuestionType[task.task_type].value(task)
    messages_to_delete = await question.send_question(call.bot, call.from_user.id)

    message_ids_to_delete = [msg.message_id for msg in messages_to_delete if msg is not None]
    await db_manager.update_user_by_id(
        call.from_user.id,
        current_task_id=task_id,
        current_messages_to_delete=message_ids_to_delete
    )

    # await call.bot.edit_message_text(f"task title: {task.title}\n"
    #                                  f"task text: {task.text}\n"
    #                                  f"task options: {task.options}\n"
    #                                  f"task input media: {task.input_media}\n",
    #                                  call.from_user.id, call.message.message_id,
    #                                  reply_markup=get_spec_current_test_task_keyboard(task))


async def handle_start_current_test_query(call: types.CallbackQuery):
    test_id = get_test_id_or_classroom_id_from_callback(call.data)
    test = await db_manager.get_test_by_id(test_id)
    tasks: list[Task] = await db_manager.get_tasks_by_test_id(test_id)
    # todo check if user has no attempts left
    # todo check deadline test
    # todo add start timer
    await db_manager.update_user_by_id(call.from_user.id, current_test_id=test_id)
    await call.bot.edit_message_text(
        test.title,
        call.from_user.id,
        call.message.message_id,
        reply_markup=get_current_test_tasks_keyboard(tasks)
    )


async def write_json_to_file(data):
    with open("data.json", "w") as f:
        f.write(data)


async def handle_refresh_test_data_query(call: types.CallbackQuery):
    test_id = get_test_id_or_classroom_id_from_callback(call.data)
    test = await db_manager.get_test_by_id(test_id)
    meta_data = await FormExtractor.extract_string(form_url=test.link)
    if not meta_data:
        await call.bot.edit_message_text(
            "unfortunately, I can't parse your Google form for some reason.",
            call.from_user.id, call.message.message_id,
            reply_markup=go_to_previous_menu_keyboard(SPEC_CREATED_TEST, [test_id]))
        return
    await db_manager.update_test_by_id(test_id, meta_data=meta_data)
    await call.bot.edit_message_text(
        "test data was successfully updated",
        call.from_user.id,
        call.message.message_id,
        reply_markup=go_to_previous_menu_keyboard(SPEC_CREATED_TEST, [test_id]))


async def handle_edit_classroom_title_query(call: types.CallbackQuery, state: FSMContext) -> None:
    classroom_id = get_test_id_or_classroom_id_from_callback(call.data)
    await call.bot.edit_message_text("enter new title", call.from_user.id, call.message.message_id)
    await state.set_state(Form.edit_classroom_title)
    await state.update_data(edit_classroom_id=classroom_id)


async def handle_edit_classroom_query(call: types.CallbackQuery):
    classroom_id = get_test_id_or_classroom_id_from_callback(call.data)
    classroom = await db_manager.get_classroom_by_id(classroom_id)
    await call.bot.edit_message_text(
        f"edit classroom \"{classroom.title}\"",
        call.from_user.id,
        call.message.message_id,
        reply_markup=get_edit_classroom_keyboard(classroom))


async def check_test_or_classroom_was_deleted_and_inform_user(entity: Test | Classroom, text,
                                                              call: types.CallbackQuery):
    if entity:
        return False
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id,
                                     reply_markup=get_go_to_main_menu_keyboard())
    return True


async def handle_spec_current_test_query(call: types.CallbackQuery):
    test_id = get_test_id_or_classroom_id_from_callback(call.data)
    test = await db_manager.get_test_by_id(test_id)

    if await check_test_or_classroom_was_deleted_and_inform_user(test, "this test was deleted", call):
        return

    await call.bot.edit_message_text(get_spec_test_info_message(test),
                                     call.from_user.id, call.message.message_id,
                                     reply_markup=get_spec_current_test_keyboard(test),
                                     parse_mode="HTML")


async def handle_change_test_status_query(call: types.CallbackQuery, new_status: TestStatus) -> None:
    test_id = get_test_id_or_classroom_id_from_callback(call.data)
    updated_values = {'status_set_by_author': new_status}
    await db_manager.update_test_by_id(test_id, **updated_values)
    test = await db_manager.get_test_by_id(test_id)

    # todo don't need to invoke get_spec_test_info_message, hjust change msg to make it quicker

    key_word = "opened" if new_status == TestStatus.AVAILABLE else "closed"

    await call.bot.edit_message_text(get_spec_test_info_message(test),
                                     call.from_user.id, call.message.message_id,
                                     reply_markup=get_spec_created_test_keyboard(test),
                                     parse_mode="HTML")

    await call.bot.answer_callback_query(call.id, f"test {key_word}")


async def handle_spec_current_classroom_query(call: types.CallbackQuery):
    classroom_id = get_test_id_or_classroom_id_from_callback(call.data)
    classroom = await db_manager.get_classroom_by_id(classroom_id)
    if not classroom:
        await call.bot.edit_message_text("this classroom was deleted", call.from_user.id, call.message.message_id,
                                         reply_markup=get_go_to_main_menu_keyboard())
        return
    author = await db_manager.get_user_by_id(classroom.author_id)

    msg = f"classroom title: {classroom.title}\n" \
          f"author: {author.name} - @{author.username}\n"

    await call.bot.edit_message_text(msg, call.from_user.id, call.message.message_id,
                                     reply_markup=go_to_previous_menu_keyboard(CURRENT_CLASSROOMS))


async def handle_current_classrooms_query(call: types.CallbackQuery) -> None:
    current_classrooms = await db_manager.get_current_classrooms_by_user_id(call.from_user.id)
    if len(current_classrooms) == 0:
        text = "you don't have current classrooms"
    else:
        text = "your current classrooms"
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id,
                                     reply_markup=get_classrooms_keyboard(current_classrooms, 'current'))


async def handle_delete_classroom_query(call: types.CallbackQuery) -> None:
    classroom_id = get_test_id_or_classroom_id_from_callback(call.data)
    classroom = await db_manager.get_classroom_by_id(classroom_id)
    await call.bot.edit_message_text(
        f"are you sure you wanna delete classroom \"{classroom.title}\"?",
        call.from_user.id,
        call.message.message_id,
        reply_markup=get_delete_entity_confirm_keyboard(Entity.CLASSROOM, classroom_id))


async def delete_classroom(classroom_id: int):
    await db_manager.delete_classroom(classroom_id)


async def handle_delete_test_query(call: types.CallbackQuery) -> None:
    test_id = get_test_id_or_classroom_id_from_callback(call.data)
    test = await db_manager.get_test_by_id(test_id)
    await call.bot.edit_message_text(
        f"are you sure you wanna delete test \"{test.title}\"?",
        call.from_user.id,
        call.message.message_id,
        reply_markup=get_delete_entity_confirm_keyboard(Entity.TEST, test_id))


async def delete_test(test_id: int):
    await db_manager.delete_test(test_id)


async def handle_delete_entity_confirm_query(call: types.CallbackQuery) -> None:
    entity, entity_id = call.data.split("#")[1:]
    print('here,', entity, Entity.CLASSROOM.value, Entity.CLASSROOM.name, Entity.CLASSROOM)
    if entity == Entity.CLASSROOM.name:
        await delete_classroom(int(entity_id))
    else:
        await delete_test(int(entity_id))
    await call.bot.edit_message_text(f"{entity} successfully deleted", call.from_user.id, call.message.message_id,
                                     reply_markup=get_go_to_main_menu_keyboard())


async def handle_show_classroom_participants_query(call: types.CallbackQuery) -> None:
    classroom_id = get_test_id_or_classroom_id_from_callback(call.data)
    classroom = await db_manager.get_classroom_by_id(classroom_id)
    participants = await db_manager.get_users_in_classroom(classroom_id)
    participants_text = "\n".join([f"{p.name} - @{p.username}" for p in participants])
    if len(participants) == 0:
        msg = "no participants yet"
    else:
        msg = f"classroom \"{classroom.title}\" participants:\n" + participants_text
    await call.bot.edit_message_text(msg, call.from_user.id, call.message.message_id,
                                     reply_markup=go_to_previous_menu_keyboard(SPEC_CREATED_CLASSROOM, [classroom_id]))


async def handle_spec_created_classroom_query(call: types.CallbackQuery):
    classroom_id = get_test_id_or_classroom_id_from_callback(call.data)
    classroom = await db_manager.get_classroom_by_id(classroom_id)
    if not classroom:
        await call.bot.edit_message_text("this classroom was deleted", call.from_user.id, call.message.message_id,
                                         reply_markup=get_go_to_main_menu_keyboard())
        return
    await call.bot.edit_message_text(f"classroom title: {classroom.title}\n"
                                     f"link: {generate_link(Entity.CLASSROOM, classroom.uuid)}",
                                     call.from_user.id, call.message.message_id,
                                     reply_markup=get_spec_classroom_keyboard(classroom))


async def handle_spec_share_test_link_to_classroom_query(call: types.CallbackQuery) -> None:
    test_id, classroom_id = call.data.split("#")[1:]
    await send_test_to_classroom_participants(test_id, classroom_id, call.bot)
    await call.bot.edit_message_text("test send to classroom participants", call.from_user.id, call.message.message_id,
                                     reply_markup=get_go_to_main_menu_keyboard())
    # await call.bot.answer_callback_query(call.id)


async def send_test_to_classroom_participants(test_id: int, classroom_id: int, bot: Bot) -> None:
    participants = await db_manager.get_users_in_classroom(classroom_id)
    for participant in participants:
        await db_manager.add_user_to_test_participants(test_id, participant.id)
        await send_message_to_user(bot, participant.id, "you have new test to pass")


async def handle_share_test_link_to_classroom_query(call: types.CallbackQuery) -> None:
    classrooms = await db_manager.get_classrooms_by_author_id(call.from_user.id)
    if len(classrooms) == 0:
        text = "you have no classrooms yet. But u can create a new one"
    else:
        text = "choose classroom"
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id,
                                     reply_markup=get_classrooms_keyboard(classrooms))
    # await call.bot.answer_callback_query(call.id)


async def handle_share_test_link_query(call: types.CallbackQuery) -> None:
    test_id = get_test_id_or_classroom_id_from_callback(call.data)
    test = await db_manager.get_test_by_id(test_id)
    created_classrooms = await db_manager.get_classrooms_by_author_id(call.from_user.id)
    await call.bot.edit_message_text(f"link: {generate_link(Entity.TEST, test.uuid)}\nchoose classroom to send test",
                                     call.from_user.id, call.message.message_id,
                                     reply_markup=get_share_test_link_to_classroom_keyboard(test_id,
                                                                                            created_classrooms))


def generate_link(type_: Entity, uuid: int) -> str:
    bot_name = os.getenv('BOT_NAME')
    if type_ == Entity.TEST:
        return f"https://t.me/{bot_name}?start=test={uuid}"
    else:
        return f"https://t.me/{bot_name}?start=class={uuid}"


async def handle_current_ended_or_with_no_attempts_tests_query(call: types.CallbackQuery) -> None:
    current_ended_or_with_no_attempts_tests = await db_manager.get_current_ended_or_with_no_attempts_tests_by_user_id(
        call.from_user.id)
    if len(current_ended_or_with_no_attempts_tests) == 0:
        text = "you don't have ended tests or they have been deleted by author"
    else:
        text = "your ended tests"
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id,
                                     reply_markup=get_current_tests_keyboard(current_ended_or_with_no_attempts_tests))


async def handle_current_available_test_with_attempts_query(call: types.CallbackQuery) -> None:
    current_available_test_with_attempts = await db_manager.get_current_available_test_with_attempts_by_user_id(
        call.from_user.id)
    if len(current_available_test_with_attempts) == 0:
        text = "you don't have current tests"
    else:
        text = "your current tests"
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id,
                                     reply_markup=get_current_tests_keyboard(current_available_test_with_attempts))


def get_spec_test_info_message(test: Test) -> str:
    msg = f"""<b>Test title:</b> {test.title}
    <b>Test duration:</b> {test.time} min
    <b>Test deadline:</b> {test.deadline}
    <b>Test attempts number:</b> {test.attempts_number}
    <b>Test status:</b> {test.status_set_by_author} {get_emoji_test_status(test.status_set_by_author)}
    <b>Test link:</b> {test.link}"""
    return msg


def get_test_id_or_classroom_id_from_callback(callback: str) -> int:
    return int(callback.split("#")[1])


async def handle_spec_created_test_query(call: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    test_id = get_test_id_or_classroom_id_from_callback(call.data)
    test = await db_manager.get_test_by_id(test_id)
    await call.bot.edit_message_text(get_spec_test_info_message(test),
                                     call.from_user.id, call.message.message_id,
                                     reply_markup=get_spec_created_test_keyboard(test),
                                     parse_mode="HTML")


async def handle_edit_test_query(call: types.CallbackQuery, state: FSMContext) -> None:
    test_id = int(call.data.split("#")[1])
    await state.clear()
    await call.bot.edit_message_text(
        "what do you want to change?",
        call.from_user.id,
        call.message.message_id,
        reply_markup=get_test_edit_keyboard(test_id))


async def handle_edit_test_something_query(
        call: types.CallbackQuery,
        state: FSMContext,
        next_state: State,
        text: str
):
    test_id = int(call.data.split("#")[1])
    await state.update_data(edit_test_id=test_id)

    await state.set_state(next_state)
    await call.bot.edit_message_text(
        text,
        call.from_user.id,
        call.message.message_id,
        reply_markup=get_test_edit_cancel_keyboard(test_id)
    )


async def handle_edit_test_title_query(call: types.CallbackQuery, state: FSMContext):
    await handle_edit_test_something_query(
        call, state, Form.edit_test_title, "type new test title"
    )


async def handle_edit_test_time_query(call: types.CallbackQuery, state: FSMContext):
    await handle_edit_test_something_query(
        call, state, Form.edit_test_time, "type new test time"
    )


async def handle_edit_test_deadline_query(call: types.CallbackQuery, state: FSMContext):
    await handle_edit_test_something_query(
        call, state, Form.edit_test_deadline, "type new test deadline"
    )


async def handle_edit_test_attempts_number_query(call: types.CallbackQuery, state: FSMContext):
    # todo check that number of attempts is not less than max number of attempts made by users already
    await handle_edit_test_something_query(
        call, state, Form.edit_test_attempts_number, "type new test attempts number"
    )


async def handle_edit_test_link_query(call: types.CallbackQuery, state: FSMContext):
    await handle_edit_test_something_query(
        call, state, Form.edit_test_link, "type new test link"
    )


@dp.message(Form.edit_classroom_title)
async def type_edit_classroom_title(message: Message, state: FSMContext):
    if not re.fullmatch(ValidationPatterns.TITLE, message.text.strip()):
        await message.answer(text="title may contain letters, digits and spaces. please, rewrite")
        return

    data = await state.get_data()
    await db_manager.update_classroom_by_id(data["edit_classroom_id"], title=message.text.strip())
    await state.clear()
    await message.answer("successfully edited")
    await message.bot.send_message(text=MAIN_MENU_TEXT, chat_id=message.from_user.id,
                                   reply_markup=get_main_menu_keyboard())


@dp.message(Form.edit_test_title)
async def type_edit_test(message: Message, state: FSMContext):
    test_title = await Validations.validate_test_title(message=message, text=message.text)
    if not test_title:
        return

    data = await state.get_data()
    await db_manager.update_test_by_id(data["edit_test_id"], title=test_title)
    await edit_test_finish(message, state, data["edit_test_id"])


@dp.message(Form.edit_test_time)
async def type_edit_test(message: Message, state: FSMContext):
    test_time = await Validations.validate_test_time(message=message, text=message.text)
    if not test_time:
        return

    data = await state.get_data()
    await db_manager.update_test_by_id(data["edit_test_id"], time=test_time)
    await edit_test_finish(message, state, data["edit_test_id"])


@dp.message(Form.edit_test_deadline)
async def type_edit_test(message: Message, state: FSMContext):
    timestamp = await Validations.validate_test_deadline(message=message, text=message.text)
    if not timestamp:
        return

    data = await state.get_data()
    await db_manager.update_test_by_id(data["edit_test_id"], deadline=timestamp)
    await edit_test_finish(message, state, data["edit_test_id"])


@dp.message(Form.edit_test_attempts_number)
async def type_edit_test(message: Message, state: FSMContext):
    test_attempts_number = await Validations.validate_test_attempts_number(message=message, text=message.text)
    if not test_attempts_number:
        return

    data = await state.get_data()
    await db_manager.update_test_by_id(data["edit_test_id"], attempts_number=test_attempts_number)
    await edit_test_finish(message, state, data["edit_test_id"])


@dp.message(Form.edit_test_link)
async def type_edit_test(message: Message, state: FSMContext):
    if not re.fullmatch(ValidationPatterns.LINK, message.text.strip()):
        await message.answer(text="please, send a correct url of the form")
        return

    data = await state.get_data()
    await message.answer(
        "now, I'll check if form could be parsed. please make sure that your form...(some constraints)",
    )
    meta_data = await FormExtractor.extract_string(form_url=message.text.strip())
    if not meta_data and "second_form_attempt" not in data:
        await message.answer(
            "unfortunately, I can't parse your Google form for some reason. "
            "try to send the link again (mind the format!). you have 1 more attempt",
        )
        await state.update_data(second_form_attempt=True)
        await message.answer(text="type test link to Google form in format...")
        return
    elif not meta_data and "second_form_attempt" in data:
        await message.answer(
            "still can't parse the form. aborting..."
        )
        await state.clear()
        await message.answer(
            "test creation aborted",
            reply_markup=get_test_edit_keyboard(data["edit_test_id"])
        )
        return

    await db_manager.update_test_by_id(data["edit_test_id"], link=message.text.strip())
    await edit_test_finish(message, state, data["edit_test_id"])


async def edit_test_finish(message: Message, state: FSMContext, test_id: int):
    await message.answer("successfully edited")
    await message.answer(
        "test edit finished",
        reply_markup=get_test_edit_keyboard(test_id)
    )
    await state.clear()


async def handle_create_test_query(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.bot.edit_message_text(
        "type test link",
        call.from_user.id,
        call.message.message_id,
    )
    await state.set_state(Form.create_test_link)


@dp.message(Form.create_test_link)
async def type_create_test(message: Message, state: FSMContext):
    if not re.fullmatch(ValidationPatterns.LINK, message.text.strip()):
        await message.answer(text="please, send a correct url of the form")
        return

    data = await state.get_data()
    await message.answer(
        "now, I'll check if form could be parsed. please make sure that your form...(some constraints)",
    )
    meta_data = await FormExtractor.extract_string(form_url=message.text.strip())
    if not meta_data and "second_form_attempt" not in data:
        await message.answer(
            "unfortunately, I can't parse your Google form for some reason. "
            "try to send the link again (mind the format!). you have 1 more attempt",
        )
        await state.update_data(second_form_attempt=True)
        await message.answer(text="type test link to Google form in format...")
        return
    elif not meta_data and "second_form_attempt" in data:
        await message.answer(
            "still can't parse the form. aborting..."
        )
        tests = await db_manager.get_tests_by_author_id(message.from_user.id)
        await state.clear()
        await message.answer(
            "test creation aborted",
            reply_markup=get_created_tests_keyboard(tests)
        )
        return

    await state.update_data(test_link=message.text.strip())
    await state.update_data(test_meta_data=meta_data)

    await message.answer(
        "do you want to add additional settings for the test?",
        reply_markup=get_created_test_additionals_keyboard()
    )


async def handle_save_test_query(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await state.clear()

    string_json = data["test_meta_data"]

    responder_uri = Translator.get_responder_uri(string_json)
    if 'title' not in data or not data['title']:
        title = Translator.get_form_title(string_json)
    else:
        title = data['title']

    tasks = await translate_to_task(string_json, call)
    if not tasks:
        return

    new_test = await db_manager.add_test(
        title=title,
        author_id=call.from_user.id,
        link=data["test_link"],
        meta_data=str(string_json),
        responder_uri=responder_uri
    )

    for task in tasks:
        await db_manager.add_task(**task, test_id=new_test.id)

    tests = await db_manager.get_tests_by_author_id(call.from_user.id)

    await call.bot.send_message(
        text="test is saved",
        chat_id=call.message.chat.id,
        reply_markup=get_created_tests_keyboard(tests)
    )


async def handle_save_test_with_additionals_query(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.create_test_title)
    await call.bot.send_message(
        text="type test title",
        chat_id=call.message.chat.id,
        reply_markup=get_created_test_cancel_addition_keyboard(skip_to_state="create_test_time")
    )


async def handle_cancel_addition_query(call: types.CallbackQuery, state: FSMContext):
    state_to_go = call.data.split("#")[1]
    if state_to_go == "create_test_save_with_additions":
        await create_test_save_with_additions(call=call, state=state)
        return

    if state_to_go in CREATION_FORMS:
        await state.set_state(CREATION_FORMS[state_to_go]["form"])

    await call.bot.send_message(
        text=CREATION_FORMS[state_to_go]["state_text"],
        chat_id=call.message.chat.id,
        reply_markup=get_created_test_cancel_addition_keyboard(
            skip_to_state=CREATION_FORMS[state_to_go]["next_state"])
    )


@dp.message(Form.create_test_title)
async def type_create_test(message: Message, state: FSMContext):
    test_title = await Validations.validate_test_title(message=message, text=message.text)
    if not test_title:
        return

    await state.update_data(test_title=test_title)
    await state.set_state(Form.create_test_time)
    await message.answer(
        text="type test duration in minutes",
        reply_markup=get_created_test_cancel_addition_keyboard(skip_to_state="create_test_deadline")
    )


@dp.message(Form.create_classroom_title)
async def type_create_classroom(message: Message, state: FSMContext):
    if not re.fullmatch(ValidationPatterns.TITLE, message.text.strip()):
        await message.answer(text="title may contain letters, digits and spaces. please, rewrite")
        return

    await state.clear()
    await db_manager.add_classroom(title=message.text.strip(), author_id=message.from_user.id)
    await message.bot.send_message(text=f"classroom \"{message.text.strip()}\" created", chat_id=message.from_user.id)
    await message.bot.send_message(text=MAIN_MENU_TEXT, chat_id=message.from_user.id,
                                   reply_markup=get_main_menu_keyboard())


@dp.message(Form.create_test_time)
async def type_create_test(message: Message, state: FSMContext):
    test_time = await Validations.validate_test_time(message=message, text=message.text)
    if not test_time:
        return

    await state.update_data(test_time=int(test_time))
    await state.set_state(Form.create_test_deadline)
    await message.answer(
        text="type test deadline in format 'DD.MM.YYYY hh:mm'",
        reply_markup=get_created_test_cancel_addition_keyboard(skip_to_state="create_test_attempts_number")
    )


@dp.message(Form.create_test_deadline)
async def type_create_test(message: Message, state: FSMContext):
    timestamp = await Validations.validate_test_deadline(message=message, text=message.text)
    if not timestamp:
        return

    await state.update_data(test_deadline_ts=timestamp)
    await state.set_state(Form.create_test_attempts_number)
    await message.answer(
        text="type test number of attempts",
        reply_markup=get_created_test_cancel_addition_keyboard(skip_to_state="create_test_save_with_additions")
    )


@dp.message(Form.create_test_attempts_number)
async def type_create_test(message: Message, state: FSMContext):
    test_attempts_number = await Validations.validate_test_attempts_number(message=message, text=message.text)
    if not test_attempts_number:
        return

    await state.update_data(test_attempts_number=int(test_attempts_number))

    # await state.set_state(Form.create_test_save_with_additions)
    # await message.answer(
    #     text="type test number of attempts",
    #     reply_markup=get_created_test_cancel_addition_keyboard(skip_to_state="create_test_save_with_additions")
    # )

    await create_test_save_with_additions(message=message, state=state)


async def translate_to_task(string_json: str, call: types.CallbackQuery):
    extractor = Translator(string_json)
    try:
        tasks: list[dict] = extractor.translate()
    except TranslationError as e:
        await call.bot.send_message(chat_id=call.from_user.id,
                                    text=f"<b>Error while translating task from form </b>:\n {e}",
                                    parse_mode="HTML")
        return
    return tasks


async def create_test_save_with_additions(state: FSMContext, message: Message = None, call: types.CallbackQuery = None):
    if message and not call:
        user_id = message.from_user.id
    elif not message and call:
        user_id = call.from_user.id
    else:
        return

    data = await state.get_data()
    params = {
        "test_title": "title",
        "test_time": "time",
        "test_deadline_ts": "deadline",
        "test_attempts_number": "attempts_number",
        "test_link": "link",
        "test_responder_uri": "responder_uri",
    }
    param_dict = {params[param]: data[param] for param in params.keys() if param in data}
    param_dict["author_id"] = user_id
    param_dict["meta_data"] = data["test_meta_data"]

    await state.clear()

    string_json = data["test_meta_data"]

    responder_uri = Translator.get_responder_uri(string_json)
    param_dict["responder_uri"] = responder_uri

    if 'title' not in param_dict or not param_dict['title']:
        param_dict["title"] = Translator.get_form_title(string_json)

    tasks = await translate_to_task(string_json, call)
    if not tasks:
        return

    new_test = await db_manager.add_test(**param_dict)

    for task in tasks:
        await db_manager.add_task(**task, test_id=new_test.id)

    await state.clear()

    tests = await db_manager.get_tests_by_author_id(user_id)

    if not call:
        await message.answer(
            text="test creation finished",
            reply_markup=get_created_tests_keyboard(tests)
        )
    else:
        await call.bot.send_message(
            text="test creation finished",
            chat_id=call.message.chat.id,
            reply_markup=get_created_tests_keyboard(tests)
        )


async def handle_create_classroom_query(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.bot.edit_message_text(
        "type classroom title",
        call.from_user.id,
        call.message.message_id,
    )
    await state.set_state(Form.create_classroom_title)


async def handle_authors_classrooms_query(call: types.CallbackQuery) -> None:
    authors_classrooms = await db_manager.get_classrooms_by_author_id(call.from_user.id)
    if len(authors_classrooms) == 0:
        text = "you have no classrooms yet. But u can create a new one"
    else:
        text = "classrooms you have created"
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id,
                                     reply_markup=get_classrooms_keyboard(authors_classrooms))


async def handle_authors_tests_query(call: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    authors_tests = await db_manager.get_tests_by_author_id(call.from_user.id)
    if len(authors_tests) == 0:
        text = "you haven't created any tests yet. But u can create a new one"
    else:
        text = "tests you have created"

    await call.bot.edit_message_text(
        text=text,
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=get_created_tests_keyboard(authors_tests)
    )


@dp.message()
async def handle_message(message: types.Message):
    user = await db_manager.get_user_by_id(message.from_user.id)
    cur_test_id = user.current_test_id
    cur_task_id = user.current_task_id

    if not cur_test_id or not cur_task_id:
        await message.bot.delete_message(message.from_user.id, message.message_id)
        return

    task = await db_manager.get_task_by_id(cur_task_id)
    if not task:
        await message.bot.edit_message_text(
            "this test was deleted by author",
            message.from_user.id,
            message.message.message_id,
            reply_markup=get_go_to_main_menu_keyboard()
        )
        return

    type_names_to_handle = QuestionType.get_names_of_types_with_message_answers()
    if task.task_type not in type_names_to_handle:
        await message.bot.delete_message(message.from_user.id, message.message_id)
        return

    question: Question = QuestionType[task.task_type].value
    if not question.is_valid_answer(message):
        await message.answer("invalid format of answer. please, try again")
        await message.bot.delete_message(message.from_user.id, message.message_id)

    user = await db_manager.get_user_by_id(message.from_user.id)
    if user.current_messages_to_delete:
        for msg_id in user.current_messages_to_delete:
            try:
                await message.bot.delete_message(message.from_user.id, msg_id)
            except Exception:
                pass

        await db_manager.update_user_by_id(message.from_user.id, current_messages_to_delete=[])

    answer = question.get_answer(message, task.id)
    await db_manager.add_answer(answer)
    await db_manager.update_user_by_id(message.from_user.id, current_task_id=None)

    test = await db_manager.get_test_by_id(cur_test_id)
    if not test:
        await message.bot.edit_message_text(
            "this test was deleted by author",
            message.from_user.id,
            message.message.message_id,
            reply_markup=get_go_to_main_menu_keyboard()
        )
        return

    await message.answer("answer saved")

    tasks: list[Task] = await db_manager.get_tasks_by_test_id(cur_test_id)
    await message.bot.send_message(
        message.from_user.id,
        test.title,
        reply_markup=get_current_test_tasks_keyboard(tasks)
    )


async def main() -> None:
    # with open(MAIN_LOG_FILE, "a") as log:
    #     if LOG_IN_FILE:
    #         logging.basicConfig(level=logging.INFO, stream=log)
    #     else:
    #         logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    bot = Bot(token=TOKEN, parse_mode="HTML")

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
