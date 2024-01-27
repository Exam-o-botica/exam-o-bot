import asyncio
import logging
import os
import sys

from aiogram import Dispatcher, Bot
from aiogram.filters import CommandStart, CommandObject

from consts import *
from keyboards import *
from src.examobot.db.manager import DBManager

# from src.main import bot, dp

TOKEN = os.getenv("EXAM_O_BOT_TOKEN")
# from src.main import db_manager
dp = Dispatcher()
db_manager = DBManager()

'''
possible start links: 
    1. https://t.me/beermovent_bot?start=test={test_id}
    2. https://t.me/beermovent_bot?start=class={classroom_id}
    
    ex1: https://t.me/beermovent_bot?start=class=5069ut54303
    ex2: https://t.me/beermovent_bot?start=test=50et3695
'''


@dp.message(CommandStart())
async def welcome_message(message: types.Message, command: CommandObject) -> None:
    name = get_user_name(message.from_user)
    exists = db_manager.check_if_user_exists(user_id=message.from_user.id)
    args = command.args
    if not exists and args:
        return  # todo add user to db and (to classroom or just test)

    elif not exists and not args:
        await db_manager.add_user(message.from_user.id, message.from_user.username, name=name)
        await message.bot.send_message(message.from_user.id, START_TEXT,
                                       reply_markup=get_go_to_main_menu_keyboard())

    elif exists and not args:
        await message.bot.send_message(message.from_user.id, START_TEXT,
                                       reply_markup=get_go_to_main_menu_keyboard())

    elif exists and args:
        return  # todo add to new class room or add new avaliable test


    # if args := command.args:
    #     pass
    # if args.startswith("class"):
    #     classroom_id = args.split("=")[1]
    #     if not db_manager.check_if_user_exists(message.from_user.id):  # added new user to db + to classroom
    #         await db_manager.add_user(message.from_user.id, message.from_user.username, name=name,
    #                                   classroom_id=classroom_id)
    #         await message.bot.send_message(message.from_user.id, START_TEXT + '\n added to classroom',
    #                                        reply_markup=get_go_to_main_menu_keyboard())
    #     else:  # added existing user to classroom
    #         user = await db_manager.get_user_by_id(message.from_user.id)
    #         if classroom_id in user.classrooms:  # check if user already in that classroom
    #             await message.bot.send_message(message.from_user.id, START_TEXT + '\n already in classroom',
    #                                            reply_markup=get_go_to_main_menu_keyboard())
    #         else:  # added existing user to classroom
    #             user.classrooms.append(classroom_id)
    #             classroom = await db_manager.get_classroom_by_id(classroom_id)
    #             classroom.participants.append(user.id)
    #             await message.bot.send_message(message.from_user.id, START_TEXT + '\n added in classroom',
    #                                            reply_markup=get_go_to_main_menu_keyboard())
    # elif args.startswith("test"):
    #     test_id = args.split("=")[1]
    #     if not db_manager.check_if_user_exists(message.from_user.id):  # added new user to db + added test
    #         await db_manager.add_user(message.from_user.id, message.from_user.username, name=name, test_id=test_id)
    #         await message.bot.send_message(message.from_user.id, START_TEXT + '\n added new test',
    #                                        reply_markup=get_go_to_main_menu_keyboard())
    #     else:
    #         user = await db_manager.get_user_by_id(message.from_user.id)
    #         if test_id in user.tests:
    #             await message.bot.send_message(message.from_user.id, START_TEXT + '\n already in test',
    #                                            reply_markup=get_go_to_main_menu_keyboard())
    #         else:
    #             await message.bot.send_message(message.from_user.id, START_TEXT + '\n added new test',
    #                                            reply_markup=get_go_to_main_menu_keyboard())
    # else:
    #     raise ValueError("wrong start link")  # todo incorrect start link

    else:
        if await db_manager.check_if_user_exists(message.from_user.id):
            await message.bot.send_message(message.from_user.id, START_TEXT,
                                           reply_markup=get_go_to_main_menu_keyboard())
        else:
            await db_manager.add_user(message.from_user.id, message.from_user.username, name=name)
            await message.bot.send_message(message.from_user.id, START_TEXT,
                                           reply_markup=get_go_to_main_menu_keyboard())


def get_user_name(user: types.User) -> str:
    name = ""
    if user.first_name:
        name += user.first_name
    if user.last_name:
        name += f" {user.last_name}"
    return name


@dp.callback_query()
async def callback_inline(call: types.CallbackQuery) -> None:
    # main menu authors options

    if call.data == BACK_TO_MAIN_MENU_CALLBACK:
        await call.bot.edit_message_text(MAIN_MENU_TEXT, call.from_user.id, call.message.message_id,
                                         reply_markup=get_main_menu_keyboard())

    elif call.data == AUTHORS_CLASSROOMS_CALLBACK:
        await handle_authors_classrooms_query(call)

    elif call.data == AUTHORS_TESTS_CALLBACK:
        await handle_authors_tests_query(call)

    elif call.data == CREATE_CLASSROOM_CALLBACK:
        await create_classroom(call)

    elif call.data == CREATE_TEST_CALLBACK:
        await create_test(call)


async def create_test(call: types.CallbackQuery) -> None:
    await db_manager.add_test(title="title test", author_id=call.from_user.id,
                              time=10, deadline=1000, attempts_number=1)
    tests = await db_manager.get_tests_by_author_id(call.from_user.id)
    await call.bot.edit_message_text("test created", call.from_user.id, call.message.message_id,
                                     reply_markup=get_tests_keyboard(tests))


async def create_classroom(call: types.CallbackQuery) -> None:
    await db_manager.add_classroom(title="title cls", author_id=call.from_user.id)
    classrooms = await db_manager.get_classrooms_by_author_id(call.from_user.id)
    await call.bot.edit_message_text("classroom created", call.from_user.id, call.message.message_id,
                                     reply_markup=get_classroom_keyboard(classrooms))


async def handle_authors_classrooms_query(call: types.CallbackQuery) -> None:
    authors_classrooms = await db_manager.get_classrooms_by_author_id(call.from_user.id)
    if len(authors_classrooms) == 0:
        text = "you have no classrooms yet. But u can create a new one"
    else:
        text = "classrooms you have created"
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id,
                                     reply_markup=get_classroom_keyboard(authors_classrooms))


async def handle_authors_tests_query(call: types.CallbackQuery) -> None:
    authors_tests = await db_manager.get_tests_by_author_id(call.from_user.id)
    if len(authors_tests) == 0:
        text = "you haven't created any tests yet. But u can create a new one"
    else:
        text = "tests you have created"
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id,
                                     reply_markup=get_tests_keyboard(authors_tests))


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
