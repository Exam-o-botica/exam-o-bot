import enum
from abc import ABC, abstractmethod

from aiogram import types, Bot

from src.examobot.db.tables import Task, Answer, AnswerStatus


class QuestionType(enum.Enum):
    STRING_OR_TEXT = enum.auto()


class Question(ABC):

    def __init__(self, task: Task) -> None:
        self.task = task

    @abstractmethod
    async def send_question(self, bot: Bot, user_id: int) -> None:
        pass

    @abstractmethod
    def validate_answer(self, message: types.Message) -> bool:
        pass

    @abstractmethod
    def get_answer(self, message: types.Message) -> None:
        """
        convert user answer message to Answer table object
        """
        pass

    @abstractmethod
    def convert_msg_to_string_repr(self, message: types.Message) -> str:
        """
            this method is needed to convert user sent message to string representation of answer
            to use in the link that we send to google form back
        """
        pass


class StringOrTextQuestion(Question):

    def __init__(self, task: Task) -> None:
        super().__init__(task)

    async def send_question(self, bot: Bot, user_id: int):
        if not self.task.input_media:
            await bot.send_message(chat_id=user_id, text=self.task.text)
            return
        await bot.send_photo(chat_id=user_id, photo=str(self.task.input_media),  # todo maybe incorrect media type
                             caption=str(self.task.text))

    def validate_answer(self, message: types.Message):
        if not message.text:
            return False

        return True

    def convert_msg_to_string_repr(self, message: types.Message) -> str:
        return message.text

    def get_answer(self, message: types.Message) -> Answer:
        return Answer(text=message.text, status=AnswerStatus.UNCHECKED,
                      task_id=self.task.id, user_id=message.from_user.id)


