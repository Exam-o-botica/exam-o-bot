import asyncio
import sys

from aiogram import types, Dispatcher, Bot
from aiogram.filters import CommandStart, CommandObject

from keyboards import *
from keyboard_texts import *
import logging
import os

from consts import *
from aiogram.filters import CommandStart, CommandObject, Command
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
    if args := command.args:
        print(args)

    await message.bot.send_message(message.from_user.id, MAIN_MENU_TEXT,
                                   reply_markup=get_main_menu_keyboard())


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
        # ask for clsroom name
        pass


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
