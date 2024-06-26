import urllib.parse
from abc import ABC, abstractmethod
from typing import Any, Callable, Generator

from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold

from examobot.db.manager import db_manager
from examobot.db.tables import Answer, AnswerStatus
from examobot.task_translator.task_keyboards import *


class FormResponseParameters:
    DEFAULT_PREFIX = "entry"

    def __init__(self, value: str = None, prefix: str = DEFAULT_PREFIX) -> None:
        self.values: list[dict[str, str]] = []
        if value:
            self.add_value(value, prefix=prefix)

    def add_value(self, value: str, prefix: str = DEFAULT_PREFIX) -> None:
        self.values.append({"prefix": prefix, "value": value})

    def add_values(self, values: list[str], prefix: str = DEFAULT_PREFIX) -> None:
        for value in values:
            self.values.append({"prefix": prefix, "value": value})

    def get_parameters(self) -> Generator[dict[str, str], None, None]:
        yield from self.values

    @staticmethod
    def from_string(value: str, prefix: str = DEFAULT_PREFIX) -> 'FormResponseParameters':
        return FormResponseParameters(value, prefix=prefix)

    @staticmethod
    def from_string_list(values: list[str], prefix: str = DEFAULT_PREFIX) -> 'FormResponseParameters':
        params = FormResponseParameters()
        params.add_values(values, prefix=prefix)
        return params


class Question(ABC):
    @staticmethod
    def get_index(option_index: str):
        return int(option_index) - 1

    @staticmethod
    async def get_text_with_options(task: Task, options: list[str]):
        text = task.text
        msg = text + "\n\nВарианты ответа:\n"
        for ind, value in enumerate(options, start=1):
            msg += f'<b>Вариант {ind}</b>: {value}\n'
        return msg

    @staticmethod
    async def check_answer_and_save(
            values_to_replace: dict[str, Any],
            user_id: int,
            task_id: int,
            answer_data_converter: Callable[[list[str]], list[str]] = None
    ) -> None:
        existing_answer = await db_manager.get_answer_by_task_id_and_user_id(
            task_id=task_id,
            user_id=user_id
        )

        if answer_data_converter:
            values_to_replace["answer_data"] = answer_data_converter(
                existing_answer.answer_data if existing_answer else []
            )

        if not existing_answer:
            answer = Answer(**values_to_replace, task_id=task_id, user_id=user_id)
            await db_manager.add_answer(answer)
            return

        await db_manager.update_answer_by_id(
            answer_id=existing_answer.id,
            dispatch_number=(existing_answer.dispatch_number + 1),
            **values_to_replace
        )

    @staticmethod
    @abstractmethod
    def needs_message_answer() -> bool:
        pass

    @staticmethod
    @abstractmethod
    async def send_question(bot: Bot, user_id: int, task: Task, menu_message_id: int) -> list[Message]:
        pass

    @staticmethod
    @abstractmethod
    def is_valid_answer(message: Message | None) -> bool:
        """
        we wanna validate messages only with text
        """
        pass

    @staticmethod
    @abstractmethod
    async def save_answer(user_ans: Message | CallbackQuery, task_id: int) -> None:
        """
        convert user answer message or callback from user to Answer table object
        """
        pass

    @staticmethod
    @abstractmethod
    def convert_answer_to_string_repr(answer: Answer, task: Task) -> FormResponseParameters:
        """
            this method is needed to convert answer to string representation of answer
            to use in the link that we send to google form back
        """
        pass

    @staticmethod
    async def send_new_or_edit_message(
            bot: Bot, menu_message_id: int,
            task: Task,
            user_id: int,
            text: str,
            keyboard: InlineKeyboardMarkup):

        messages_to_delete = []
        if not task.input_media:
            await bot.edit_message_text(
                chat_id=user_id,
                message_id=menu_message_id,
                text=text,
                reply_markup=keyboard
            )

        else:
            await bot.delete_message(
                chat_id=user_id,
                message_id=menu_message_id
            )
            msg1 = await bot.send_photo(
                chat_id=user_id,
                photo=str(task.input_media)
            )  # todo maybe incorrect media type
            messages_to_delete.append(msg1)

            await bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=keyboard
            )
        return messages_to_delete


class StringOrTextQuestion(Question):

    @staticmethod
    def needs_message_answer() -> bool:
        return True

    @staticmethod
    async def send_question(bot: Bot, user_id: int, task: Task, menu_message_id: int):
        question_text = task.text + "\n" + hbold("Запомнен будет последний данный ответ")
        messages_to_delete = await Question.send_new_or_edit_message(
            bot=bot,
            menu_message_id=menu_message_id,
            task=task,
            user_id=user_id,
            text=question_text,
            keyboard=get_no_options_keyboard(task)
        )
        return messages_to_delete

    @staticmethod
    def is_valid_answer(message: Message):
        # todo invoke this function after user sent a message, user has current
        #  test id and current task id flags in db and the type of current task is STRING_OR_TEXT
        if not message.text:
            return False

        return True

    @staticmethod
    async def save_answer(user_ans: Message | CallbackQuery, task_id: int) -> None:
        if not isinstance(user_ans, Message):
            raise AssertionError(
                f"user_ans expected as aiogram.types.Message, found: {type(user_ans)}")

        values = {
            "answer_data": [user_ans.text],
            "status": AnswerStatus.SAVED,
        }
        await Question.check_answer_and_save(
            values_to_replace=values,
            user_id=user_ans.from_user.id,
            task_id=task_id
        )

    @staticmethod
    def convert_answer_to_string_repr(answer: Answer, task: Task) -> FormResponseParameters:
        params = FormResponseParameters(
            urllib.parse.quote_plus(answer.answer_data[0])
        )
        return params


class OneChoiceQuestion(Question):
    @staticmethod
    def needs_message_answer() -> bool:
        return False

    @staticmethod
    async def send_question(bot: Bot, user_id: int, task: Task, menu_message_id: int) -> list[Message]:
        options = task.options
        if not options:
            raise AssertionError("Expected answer options in this type of questions")

        answer = await db_manager.get_answer_by_task_id_and_user_id(task.id, user_id)
        chosen_variant = -1 \
            if not answer or answer.status == AnswerStatus.UNCHECKED \
            else int(answer.answer_data[0])

        text = await Question.get_text_with_options(task, options)
        messages_to_delete = await Question.send_new_or_edit_message(
            bot=bot,
            menu_message_id=menu_message_id,
            task=task,
            user_id=user_id,
            text=text,
            keyboard=get_one_choice_keyboard(task, len(options), chosen_variant)
        )
        return messages_to_delete

    @staticmethod
    def is_valid_answer(message: Message | None) -> bool:
        return True

    @staticmethod
    async def save_answer(user_ans: Message | CallbackQuery, task_id: int) -> None:
        if not isinstance(user_ans, CallbackQuery):
            raise AssertionError(
                f"user_ans expected as aiogram.CallbackQuery, found: {type(user_ans)}")

        user_chosen_variant = user_ans.data.split('#')[-1]
        values = {
            "answer_data": [user_chosen_variant],
            "status": AnswerStatus.SAVED,
        }
        await Question.check_answer_and_save(
            values_to_replace=values, task_id=task_id, user_id=user_ans.from_user.id)

    @staticmethod
    def convert_answer_to_string_repr(answer: Answer, task: Task) -> FormResponseParameters:
        true_answer = task.options[
            Question.get_index(answer.answer_data[0])
        ]
        params = FormResponseParameters(
            urllib.parse.quote_plus(true_answer)
        )
        return params


class MultipleChoiceQuestion(Question):

    @staticmethod
    def needs_message_answer() -> bool:
        return False

    @staticmethod
    async def send_question(bot: Bot, user_id: int, task: Task, menu_message_id: int) -> list[Message]:
        options = task.options
        if not options:
            raise AssertionError("Expected answer options in this type of questions")

        answer: Answer = await db_manager.get_answer_by_task_id_and_user_id(task.id, user_id)
        chosen_options = [] \
            if not answer or answer.status == AnswerStatus.UNCHECKED \
            else [int(option) for option in answer.answer_data]

        text = await Question.get_text_with_options(task, options)

        messages_to_delete = await Question.send_new_or_edit_message(
            bot=bot,
            menu_message_id=menu_message_id,
            task=task,
            user_id=user_id,
            text=text,
            keyboard=get_multiple_choice_keyboard(task, len(options), chosen_options)
        )
        return messages_to_delete

    @staticmethod
    def is_valid_answer(message: Message | None) -> bool:
        return True

    @staticmethod
    async def save_answer(user_ans: Message | CallbackQuery, task_id: int) -> None:
        if not isinstance(user_ans, CallbackQuery):
            raise AssertionError(f"user_ans expected as CallbackQuery, found: {type(user_ans)}")

        new_chosen_option = user_ans.data.split("#")[-1]

        def convert_answer_data(data: list[str]) -> list[str]:
            data_set = set(data)
            if new_chosen_option in data_set:
                data_set.remove(new_chosen_option)
            else:
                data_set.add(new_chosen_option)

            return list(data_set)

        values = {
            "answer_data": [],
            "status": AnswerStatus.SAVED,
        }
        await Question.check_answer_and_save(
            values_to_replace=values,
            task_id=task_id,
            user_id=user_ans.from_user.id,
            answer_data_converter=convert_answer_data
        )

    @staticmethod
    def convert_answer_to_string_repr(answer: Answer, task: Task) -> FormResponseParameters:
        task_options = task.options
        true_answers = [task_options[Question.get_index(i)] for i in answer.answer_data]
        return FormResponseParameters.from_string_list(
            [urllib.parse.quote_plus(ans) for ans in true_answers]
        )
