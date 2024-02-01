import enum
from abc import ABC, abstractmethod

from aiogram import types, Bot

from src.examobot.db.tables import Task, Answer, AnswerStatus
from src.examobot.task_translator.task_keyboards import get_one_choice_keyboard
from src.examobot.bot import db_manager


class QuestionType(enum.Enum):
    STRING_OR_TEXT = enum.auto()


class Question(ABC):

    def __init__(self, task: Task) -> None:
        self.task = task

    @staticmethod
    async def get_options_text(options: list[str]):
        msg = "Варианты ответа:\n"
        for ind, value in enumerate(options):
            msg += f'<b>Вариант {ind}</b>: {value}\n'
        return msg

    @abstractmethod
    async def send_question(self, bot: Bot, user_id: int) -> None:
        pass

    @staticmethod
    @abstractmethod
    def validate_answer(message: types.Message | None) -> bool:
        """
        we wanna validate messages only with text
        """
        pass

    @staticmethod
    @abstractmethod
    def get_answer(user_ans: types.Message | types.CallbackQuery, task_id: int) -> Answer:
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

    def __init__(self, task: Task) -> None:
        super().__init__(task)

    async def send_question(self, bot: Bot, user_id: int):
        # todo we need to put a flag in db with current test id and current task id
        if not self.task.input_media:
            await bot.send_message(chat_id=user_id, text=self.task.text)
            return
        await bot.send_photo(chat_id=user_id,
                             photo=str(self.task.input_media),  # todo maybe incorrect media type
                             caption=str(self.task.text))

    @staticmethod
    def validate_answer(message: types.Message):
        # todo invoke this function after user sent a message, user has current
        #  test id and current task id flags in db and the type of current task is STRING_OR_TEXT
        if not message.text:
            return False

        return True

    def convert_answer_to_string_repr(self, answer: Answer) -> str:
        pass
        # todo

    @staticmethod
    def get_answer(message: types.Message, task_id) -> Answer:
        return Answer(answer_data=[message.text], status=AnswerStatus.UNCHECKED,
                      task_id=task_id, user_id=message.from_user.id)


class OneChoiceQuestion(Question):
    def __init__(self, task: Task) -> None:
        super().__init__(task)

    async def send_question(self, bot: Bot, user_id: int) -> None:
        options = self.task.options
        if not options:
            raise AssertionError("Expected answer options in this type of questions")

        text = self.get_options_text(options)
        answer = await db_manager.get_answer_by_task_id_and_user_id(self.task.id, user_id)
        if answer.status == AnswerStatus.UNCHECKED:
            chosen_variant = -1
        else:
            chosen_variant = int(answer.answer_data[0])

        if not self.task.input_media:
            await bot.send_message(chat_id=user_id, text=text,
                                   reply_markup=get_one_choice_keyboard(self.task.id, len(options), chosen_variant))
            return

        await bot.send_photo(chat_id=user_id,
                             photo=str(self.task.input_media),  # todo maybe incorrect media type
                             caption=str(text),
                             reply_markup=get_one_choice_keyboard(self.task.id, len(options), chosen_variant))

    @staticmethod
    def validate_answer(message: types.Message | None) -> bool:
        return True

    @staticmethod
    def get_answer(user_ans: types.CallbackQuery, task_id: int) -> Answer:
        if not user_ans.isinstance(types.CallbackQuery):
            raise AssertionError(f"user_ans expected as types.CallbackQuery, found: {type(user_ans)}")

        user_chosen_variant = user_ans.data.split('#')[-1]
        return Answer(answer_data=[user_chosen_variant],
                      status=AnswerStatus.CHOSEN,
                      task_id=task_id,
                      user_id=user_ans.from_user.id)

    def convert_answer_to_string_repr(self, answer: Answer) -> str:
        pass
