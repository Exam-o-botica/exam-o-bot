import enum

from src.examobot.task_translator.questions_classes import *


class QuestionType(enum.Enum):
    STRING_OR_TEXT = StringOrTextQuestion
    ONE_CHOICE = OneChoiceQuestion
    MULTIPLE_CHOICE = MultipleChoiceQuestion
