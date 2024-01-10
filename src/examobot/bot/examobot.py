import enum
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, ReplyKeyboardRemove

from examobot.bot.bot_utils import *
from examobot.db.manager import DBManager


class States(StatesGroup):
    initial = State()
    role = State()
    test = State()
    task = State()
    handle_task_answer = State()


class Roles(enum.Enum):
    STUDENT = "Student"
    TEST_AUTHOR = "Test author"


class MenuOptions(enum.Enum):
    START = "Start"
    GO_BACK_TO_TEST_MENU = "Go to the test menu"
    GO_BACK_TO_INIT_MENU = "Go to the main menu"


# TODO Сделать ChatMemberUpdated функцию для обработки новичков (Можно было бы добавлять в БД)
class ExamOBot:

    def __init__(self, token: str, dispatcher: Dispatcher, db_manager: DBManager) -> None:
        self.bot = Bot(token, parse_mode=ParseMode.HTML)
        self.db_manager: DBManager = db_manager
        self.dp: Dispatcher = dispatcher
        self.help = HelpMaker.make_help_list(self)

        self.dp.message(Command("help"))(self.command_help_handler)
        self.dp.message(CommandStart())(self.command_start_handler)
        self.dp.message(Command("exit"))(
            self.dp.message(F.text.casefold() == "exit")(
                self.command_exit_handler
            )
        )

        self.dp.message(States.role)(self.state_role_handler)
        self.role_value_handlers: dict[str, tp.Callable[[tp.Any, tp.Any], tp.Any]] = {
            Roles.STUDENT.value: self.state_all_tests_handler,
            Roles.TEST_AUTHOR.value: self.state_test_author_handler
        }

        self.dp.message(
            States.test, F.text.casefold() == MenuOptions.GO_BACK_TO_INIT_MENU.value.lower()
        )(self.command_exit_handler)
        self.dp.message(States.test)(self.state_test_handler)

        self.dp.message(
            States.task, F.text.casefold() == MenuOptions.START.value.lower()
        )(self.state_task_handler)
        self.dp.message(
            States.task, F.text.casefold() == MenuOptions.GO_BACK_TO_INIT_MENU.value.lower()
        )(self.command_exit_handler)
        self.dp.message(
            States.task, F.text.casefold() == MenuOptions.GO_BACK_TO_TEST_MENU.value.lower()
        )(self.state_all_tests_handler)

        self.dp.message(States.handle_task_answer)(self.state_handle_task_answer_handler)

    async def command_start_handler(self, message: Message, state: FSMContext) -> None:
        """
        Greets user.
        :RU Приветствует пользователя.

        :param message: message received
        :param state: new state
        :return: None
        """

        await state.update_data(chat_id=message.chat.id)
        data = await state.get_data()

        if "not_initial" not in data:
            await state.update_data(not_initial=True)
            await message.answer(
                RepresentationUtils.make_start_reply(message.from_user.full_name)
            )

        await state.set_state(States.role)
        await message.answer(
            f"What's your role?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=role.value)] for role in Roles],
                resize_keyboard=True,
            ),
        )

    async def state_role_handler(self, message: Message, state: FSMContext) -> None:
        role = message.text.strip()
        await state.update_data(role=role)  # Possible leak
        await self.role_value_handlers[role](message, state)

    async def state_all_tests_handler(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        if "tests" in data:
            tests = data["tests"]
        else:
            tests = await self.db_manager.get_test_titles()
            await state.update_data(test_titles=tests)

        await state.set_state(States.test)

        buttons = [[KeyboardButton(text=test.title)] for test in tests]
        buttons.append([KeyboardButton(text=MenuOptions.GO_BACK_TO_INIT_MENU.value)])
        await message.answer(
            "Select test from the list",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=buttons,
                resize_keyboard=True,
            ),
        )

    async def state_test_handler(self, message: Message, state: FSMContext) -> None:
        test, author = await self.db_manager.get_test_and_author_by_test_title(message.text)
        if not test:
            await message.answer("There is no such test")
            return

        participations = await self.db_manager.get_participations_by_test_id_and_tg_id(test.id, message.from_user.id)
        if len(participations) >= test.attempts_number:
            await message.answer(
                f"{hbold(test.title)}\n"
                f"Unfortunately, you don't have attempts left"
            )
            await self.state_all_tests_handler(message, state)
            return

        await state.update_data(test=test)

        tasks = await self.db_manager.get_tasks_by_test_id(test.id)
        await message.answer(
            RepresentationUtils.make_test_info_reply(test, author, tasks, participations))

        await state.update_data(tasks=tasks)
        await state.set_state(States.task)
        await message.answer(
            "Press button to start.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text=MenuOptions.START.value)],
                    [KeyboardButton(text=MenuOptions.GO_BACK_TO_TEST_MENU.value)],
                    [KeyboardButton(text=MenuOptions.GO_BACK_TO_INIT_MENU.value)],
                ],
                resize_keyboard=True,
            ),
        )

    async def state_task_handler(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        if "task_view_started" not in data or not data["task_view_started"]:
            await state.update_data(task_view_started=True, task_view_order_index=0)
            await self.db_manager.add_participation(data["test"].id, message.from_user.id)
            order_index = 0
        else:
            order_index = data["task_view_order_index"]
            if order_index == len(data["tasks"]):
                await state.update_data(task_view_started=False)
                await message.answer("The test is over. Your answers are stored. Thank you for participation")
                await self.state_all_tests_handler(message, state)
                return

        task = data["tasks"][order_index]
        # TODO Photos handling
        await message.answer(
            RepresentationUtils.make_task_info_reply(task),
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(States.handle_task_answer)

    async def state_handle_task_answer_handler(self, message: Message, state: FSMContext) -> None:
        await message.answer("Handle answer")

        data = await state.get_data()
        await state.update_data(task_view_order_index=(data["task_view_order_index"] + 1))

        await state.set_state(States.task)
        await self.state_task_handler(message, state)

    async def state_test_author_handler(self, message: Message, state: FSMContext) -> None:
        await message.answer(Roles.TEST_AUTHOR.value)

    async def command_exit_handler(self, message: Message, state: FSMContext) -> None:
        """
        Allows to cancel current dialog and go back to initial menu.

        :RU Позволяет прервать текущий диалог и вернуться в начальное меню.
        """
        current_state = await state.get_state()
        if current_state is not None:
            logging.info("Cancelling state %r", current_state)
            await message.answer(MenuOptions.GO_BACK_TO_INIT_MENU.value)

        await self.reset_state_data(state)

        await state.set_state(States.initial)
        await self.command_start_handler(message, state)

    async def command_help_handler(self, message: Message) -> None:
        """
        Shows a list of available commands.
        :RU Показывает список доступных команд.

        :param message: message received
        :return: None
        """
        await message.answer(self.help)

    async def run(self) -> None:
        await self.dp.start_polling(self.bot)

    async def reset_state_data(self, state: FSMContext):
        await state.update_data(test=None, tasks=None, test_titles=None)
