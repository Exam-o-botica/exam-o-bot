import asyncio
import sys

from aiogram import types, Dispatcher, Bot
from aiogram.filters import CommandStart, CommandObject

from keyboards import get_start_keyboard
from keyboard_texts import *
import logging
import os

from src.examobot.db.manager import DBManager

# from src.main import bot, dp

TOKEN = os.getenv("EXAM_O_BOT_TOKEN")
# from src.main import db_manager
dp = Dispatcher()
db_manager = DBManager()


@dp.message(CommandStart())
async def welcome_message(message: types.Message, command: CommandObject) -> None:

    if args := command.args:
        pass  # add to classroom

    await message.bot.send_message(message.from_user.id, "hey, choose your role",
                                   reply_markup=get_start_keyboard())


@dp.callback_query()
async def callback_inline(call: types.CallbackQuery) -> None:
    if call.data == STUDENT_CALLBACK:
        await call.bot.edit_message_text("you are student", call.from_user.id, call.message.message_id)

    elif call.data == TEACHER_CALLBACK:
        await call.bot.edit_message_text("you are teacher", call.from_user.id, call.message.message_id)


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
