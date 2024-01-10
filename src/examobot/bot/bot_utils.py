import inspect
import re
import typing as tp

from aiogram.utils.markdown import hbold
from sqlalchemy import Row, RowMapping


class RepresentationUtils:
    DEFAULT_REPLY = "Что-то пошло не так. Попробуй еще раз."

    @staticmethod
    def make_start_reply(name: str) -> str:
        return f"Привет, {hbold(name)}! " + \
            f"" + \
            f"Напиши /help, чтобы увидеть список всех доступных команд."

    @staticmethod
    def make_i_expected_reply(right_type: str):
        return f"Я ожидал {right_type.lower()}."

    @staticmethod
    def make_test_info_reply(test: tp.Optional[tp.Any],
                             author: tp.Optional[tp.Any],
                             tasks: tp.Sequence[tp.Union[Row, RowMapping]],
                             participations: tp.Sequence[tp.Union[Row, RowMapping]]):
        reply = f"{hbold(test.title)}\n" + \
                f"Author: {author.first_name} {author.last_name}\n" + \
                f"Duration: {test.time}\n" + \
                f"Number of tasks: {len(tasks)}\n" + \
                f"Attempts: {test.attempts_number - len(participations)}/{test.attempts_number}"

        return reply

    @staticmethod
    def make_task_info_reply(task: tp.Any):
        reply = f"{hbold(task.title)}\n" + \
                f"{task.text}"

        return reply


class HelpMaker:
    PREFIX = "command_"
    SUFFIX = "_handler"
    DEFAULT_REPLY = "Название говорящее."
    HIDDEN_COMMANDS = {"start"}

    @staticmethod
    def extract_locale_doc(doc: str, locale: str = "RU") -> str:
        description = HelpMaker.DEFAULT_REPLY

        doc_parts = doc.split(":")
        if len(doc_parts) == 0 or len(doc_parts) == 1:
            return description

        for part in doc_parts:
            if part.startswith(locale):
                description = part.removeprefix(locale)
                break

        return re.sub(r"\s+", " ", description.strip())

    @staticmethod
    def make_help_list(bot: tp.Any) -> str:
        message = ""
        methods = inspect.getmembers(bot, predicate=inspect.ismethod)
        for method in methods:
            if method[0].startswith(HelpMaker.PREFIX) and method[0].endswith(HelpMaker.SUFFIX):
                command_name = method[0].removeprefix(HelpMaker.PREFIX).removesuffix(HelpMaker.SUFFIX)
                if command_name in HelpMaker.HIDDEN_COMMANDS:
                    continue

                command_doc = HelpMaker.extract_locale_doc(method[1].__doc__)
                message += "/" + command_name + " - "
                message += command_doc + "\n\n"

        return message.removesuffix("\n\n")
