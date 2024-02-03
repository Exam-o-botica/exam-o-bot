from abc import ABC, abstractmethod
from typing import Any, Callable

from aiogram import Bot
from aiogram.types import Message, CallbackQuery

from src.examobot.db.manager import db_manager
from src.examobot.db.tables import Answer, AnswerStatus
from src.examobot.task_translator.task_keyboards import *


# from src.examobot.bot import db_manager


class Question(ABC):
    @staticmethod
    async def get_options_text(options: list[str]):
        msg = "Варианты ответа:\n"
        for ind, value in enumerate(options):
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

        if not existing_answer:
            answer = Answer(**values_to_replace, task_id=task_id, user_id=user_id)
            await db_manager.add_answer(answer)
            return

        if answer_data_converter:
            values_to_replace["answer_data"] = answer_data_converter(existing_answer.answer_data)

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
    async def send_question(bot: Bot, user_id: int, task: Task) -> list[Message]:
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

    @abstractmethod
    def convert_answer_to_string_repr(self, answer: Answer) -> str:
        """
            this method is needed to convert answer to string representation of answer
            to use in the link that we send to google form back
        """
        pass


class StringOrTextQuestion(Question):

    @staticmethod
    def needs_message_answer() -> bool:
        return True

    @staticmethod
    async def send_question(bot: Bot, user_id: int, task: Task):
        messages_to_delete = []
        if task.input_media:
            msg1 = await bot.send_photo(
                chat_id=user_id,
                photo=str(task.input_media)
            )
            messages_to_delete.append(msg1)

        msg2 = await bot.send_message(
            chat_id=user_id,
            text=task.text,
            reply_markup=get_no_options_keyboard(task)
        )
        messages_to_delete.append(msg2)
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

    def convert_answer_to_string_repr(self, answer: Answer) -> str:
        pass
        # todo


class OneChoiceQuestion(Question):
    @staticmethod
    def needs_message_answer() -> bool:
        return False

    @staticmethod
    async def send_question(bot: Bot, user_id: int, task: Task) -> list[Message]:
        options = task.options
        if not options:
            raise AssertionError("Expected answer options in this type of questions")

        text = await Question.get_options_text(options)
        answer = await db_manager.get_answer_by_task_id_and_user_id(task.id, user_id)
        chosen_variant = -1 \
            if not answer or answer.status == AnswerStatus.UNCHECKED \
            else int(answer.answer_data[0])

        task = await db_manager.get_task_by_id(task.id)
        messages_to_delete = []
        if task.input_media:
            msg1 = await bot.send_photo(
                chat_id=user_id,
                photo=str(task.input_media)
            ),  # todo maybe incorrect media type
            messages_to_delete.append(msg1)

        msg2 = await bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=get_one_choice_keyboard(task, len(options), chosen_variant)
        )
        messages_to_delete.append(msg2)
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

    def convert_answer_to_string_repr(self, answer: Answer) -> str:
        pass


class MultipleChoiceQuestion(Question):

    @staticmethod
    def needs_message_answer() -> bool:
        return False

    @staticmethod
    async def send_question(bot: Bot, user_id: int, task: Task) -> list[Message]:
        options = task.options
        if not options:
            raise AssertionError("Expected answer options in this type of questions")

        text = await Question.get_options_text(options)

        answer: Answer = await db_manager.get_answer_by_task_id_and_user_id(task.id, user_id)
        chosen_options = [] \
            if not answer or answer.status == AnswerStatus.UNCHECKED \
            else [int(option) for option in answer.answer_data]

        messages_to_delete = []
        if task.input_media:
            msg1 = await bot.send_photo(
                chat_id=user_id,
                photo=str(task.input_media)
            )
            messages_to_delete.append(msg1)

        msg2 = await bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=get_multiple_choice_keyboard(task, len(options), chosen_options)
        )
        messages_to_delete.append(msg2)
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

    def convert_answer_to_string_repr(self, answer: Answer) -> str:
        pass
