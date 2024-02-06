import enum

from examobot.task_translator.questions_classes import *


class QuestionType(enum.Enum):
    STRING_OR_TEXT = StringOrTextQuestion
    ONE_CHOICE = OneChoiceQuestion
    MULTIPLE_CHOICE = MultipleChoiceQuestion

    @staticmethod
    def get_names_of_types_with_message_answers() -> set[str]:
        types_with_message_answers_names = set()
        for type_ in QuestionType:
            if type_.value.needs_message_answer():
                types_with_message_answers_names.add(type_.name)

        return types_with_message_answers_names
