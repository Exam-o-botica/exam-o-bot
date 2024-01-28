import asyncio
import logging
import os
import re
import sys

from aiogram import Dispatcher, Bot, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from consts import *
from keyboards import *
from src.examobot.form_handlers import *
from src.examobot.db.manager import DBManager

# from src.main import bot, dp

TOKEN = os.getenv("EXAM_O_BOT_TOKEN")
# from src.main import db_manager
dp = Dispatcher()
db_manager = DBManager()


class Form(StatesGroup):
    test_title = State()
    test_time = State()
    test_deadline = State()
    test_attempts_number = State()
    test_link = State()
    test_save = State()


'''
possible start links: 
    1. https://t.me/beermovent_bot?start=test={test_id}
    2. https://t.me/beermovent_bot?start=class={classroom_id}
    
    ex1: https://t.me/beermovent_bot?start=class=5069ut54303
    ex2: https://t.me/beermovent_bot?start=test=50et3695
'''


def valid_link(link, type):
    regex = re.compile(f'{type}=' + '[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
    match = regex.match(link)
    return bool(match)


@dp.message(CommandStart())
async def welcome_message(message: types.Message, command: CommandObject) -> None:
    name = get_user_name(message.from_user)
    exists = await db_manager.check_if_user_exists(user_id=message.from_user.id)
    args = command.args

    if not exists:
        await db_manager.add_user(message.from_user.id, message.from_user.username, name=name)
        await message.bot.send_message(message.from_user.id, START_TEXT)

    if args:
        if valid_link(args, "class"):
            classroom_uuid = args.split("=")[1]
            classroom = await db_manager.get_classroom_by_uuid(classroom_uuid)

            if not classroom:
                await message.bot.send_message(message.from_user.id, "this classroom doesn't exist",
                                               reply_markup=get_go_to_main_menu_keyboard())
                return

            if await db_manager.check_if_user_in_classroom(classroom.id,
                                                           message.from_user.id):  # todo maybe we wanna consider that user is not author of this classroom
                await message.bot.send_message(message.from_user.id, "you are already joined this classroom",
                                               reply_markup=get_go_to_main_menu_keyboard())
                return

            await db_manager.add_user_to_classroom(classroom.id,
                                                   message.from_user.id)
            await message.bot.send_message(message.from_user.id,
                                           SUCCESSFULLY_ADDED_TO_CLASSROOM.format(classroom.title),
                                           reply_markup=get_go_to_main_menu_keyboard())

        elif valid_link(args, "test"):
            test_uuid = args.split("=")[1]
            test = await db_manager.get_test_by_uuid(test_uuid)
            if not test:
                await message.bot.send_message(message.from_user.id, "link is invalid, test doesn't exist",
                                               reply_markup=get_go_to_main_menu_keyboard())
                return

            if await db_manager.check_if_user_in_test(test.id,
                                                      message.from_user.id):  # todo maybe we wanna consider that user is not author of this test
                await message.bot.send_message(message.from_user.id, "you are already able to pass this test",
                                               reply_markup=get_go_to_main_menu_keyboard())
                return

            await db_manager.add_user_to_test_participants(test.id, message.from_user.id)

            await message.bot.send_message(message.from_user.id,
                                           SUCCESSFULLY_ADDED_TO_TESTS.format(test.title),
                                           reply_markup=get_go_to_main_menu_keyboard())

        else:
            await message.bot.send_message(message.from_user.id, "link is invalid",
                                           reply_markup=get_go_to_main_menu_keyboard())

    else:
        await message.bot.send_message(message.from_user.id, MAIN_MENU_TEXT,
                                       reply_markup=get_main_menu_keyboard())


def get_user_name(user: types.User) -> str:
    name = ""
    if user.first_name:
        name += user.first_name
    if user.last_name:
        name += f" {user.last_name}"
    return name


@dp.callback_query()
async def callback_inline(call: types.CallbackQuery, state: FSMContext) -> None:
    # main menu authors options

    if call.data == BACK_TO_MAIN_MENU_CALLBACK:
        await call.bot.edit_message_text(MAIN_MENU_TEXT, call.from_user.id, call.message.message_id,
                                         reply_markup=get_main_menu_keyboard())

    elif call.data == AUTHORS_CLASSROOMS_CALLBACK:
        await handle_authors_classrooms_query(call)

    elif call.data == CREATE_CLASSROOM_CALLBACK:
        await create_classroom(call)

    # TESTS

    elif call.data == CREATE_TEST_CALLBACK:
        await create_test(call, state)

    elif call.data == AUTHORS_TESTS_CALLBACK:
        await handle_authors_tests_query(call)

    elif SPEC_CREATED_TEST_CALLBACK in call.data:
        await handle_spec_created_test_query(call)


def get_spec_test_info_message(test: Test) -> str:
    msg = f"""<b>Test title:</b> {test.title}
    <b>Test duration:</b> {test.time} min
    <b>Test deadline:</b> {test.deadline}
    <b>Test attempts number:</b> {test.attempts_number}
    <b>Test status:</b> {test.status_set_by_author}
    <b>Test link:</b> {test.link}"""
    return msg


def get_test_id_or_classroom_id_from_callback(callback: str) -> int:
    return int(callback.split("#")[1])


async def handle_spec_created_test_query(call: types.CallbackQuery) -> None:
    test_id = get_test_id_or_classroom_id_from_callback(call.data)
    test = await db_manager.get_test_by_id(test_id)
    await call.bot.edit_message_text(get_spec_test_info_message(test),
                                     call.from_user.id, call.message.message_id,
                                     reply_markup=get_spec_created_test_keyboard(test),
                                     parse_mode="HTML")



async def create_test(call: types.CallbackQuery, state: FSMContext) -> None:
    # await db_manager.add_test(
    #     title="title test",
    #     author_id=call.from_user.id,
    #     time=10,
    #     deadline=1000,
    #     attempts_number=1
    # )
    # tests = await db_manager.get_tests_by_author_id(call.from_user.id)
    await call.bot.edit_message_text(
        "type test title",
        call.from_user.id,
        call.message.message_id,
        # reply_markup=get_tests_keyboard(tests)
    )
    await state.set_state(Form.test_title)


@dp.message(Form.test_title, F.text.regexp(r"^\s*\w+(\s+\w+)*\s*$"))
async def type_test_title(message: Message, state: FSMContext):
    await state.update_data(test_title=message.text.strip())
    await state.set_state(Form.test_time)
    await message.answer(text="type test duration in minutes")


@dp.message(Form.test_time, F.text.regexp(r"^\s*\d+\s*$"))
async def type_test_time(message: Message, state: FSMContext):
    await state.update_data(test_time=message.text.strip())
    await state.set_state(Form.test_deadline)
    await message.answer(text="type test deadline")


# TODO Make the regex suitable for form-links
@dp.message(Form.test_deadline)
async def type_test_deadline(message: Message, state: FSMContext):
    await state.update_data(test_deadline=message.text.strip())
    await state.set_state(Form.test_attempts_number)
    await message.answer(text="type test number of attempts")


@dp.message(Form.test_attempts_number, F.text.regexp(r"^\s*\d+\s*$"))
async def type_test_attempts_number(message: Message, state: FSMContext):
    await state.update_data(test_attempts_number=message.text.strip())
    await state.set_state(Form.test_link)
    await message.answer(text="type test link to Google form in format...")


# TODO Make the regex suitable for form-links
@dp.message(Form.test_link)
async def type_test_attempts_number(message: Message, state: FSMContext):
    await state.update_data(test_link=message.text.strip())
    await state.set_state(Form.test_save)
    await message.answer(text="thanks a lot")
    await test_save(message, state)


async def test_save(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.answer(
        "form processing could take some time :(",
    )
    meta_data = await FormExtractor.extract(form_url=data["test_link"])
    if not meta_data and "second_form_attempt" not in data:
        await message.answer(
            "unfortunately, I can't parse your Google form for some reason. "
            "try to send the link again (mind the format!)",
        )
        await state.update_data(second_form_attempt=True)
        await state.set_state(Form.test_link)
        await message.answer(text="type test link to Google form in format...")
        return
    elif not meta_data and "second_form_attempt" in data:
        await message.answer(
            "still can't parse the form. aborting..."
        )
    else:
        await db_manager.add_test(
            title=data["test_title"],
            author_id=message.from_user.id,
            time=int(data["test_time"]),
            deadline=int(data["test_deadline"]),
            attempts_number=int(data["test_attempts_number"]),
            link=data["test_link"],
            meta_data=meta_data,
        )
        await message.answer(meta_data)

    tests = await db_manager.get_tests_by_author_id(message.from_user.id)
    await message.answer(
        "test creation finished",
        reply_markup=get_created_tests_keyboard(tests)
    )
    await state.clear()


async def create_classroom(call: types.CallbackQuery) -> None:
    await db_manager.add_classroom(title="title cls", author_id=call.from_user.id)
    classrooms = await db_manager.get_classrooms_by_author_id(call.from_user.id)
    await call.bot.edit_message_text("classroom created", call.from_user.id, call.message.message_id,
                                     reply_markup=get_created_classrooms_keyboard(classrooms))


async def handle_authors_classrooms_query(call: types.CallbackQuery) -> None:
    authors_classrooms = await db_manager.get_classrooms_by_author_id(call.from_user.id)
    if len(authors_classrooms) == 0:
        text = "you have no classrooms yet. But u can create a new one"
    else:
        text = "classrooms you have created"
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id,
                                     reply_markup=get_created_classrooms_keyboard(authors_classrooms))


async def handle_authors_tests_query(call: types.CallbackQuery) -> None:
    authors_tests = await db_manager.get_tests_by_author_id(call.from_user.id)
    if len(authors_tests) == 0:
        text = "you haven't created any tests yet. But u can create a new one"
    else:
        text = "tests you have created"
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id,
                                     reply_markup=get_created_tests_keyboard(authors_tests))


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
