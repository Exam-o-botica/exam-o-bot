import json

from examobot.task_translator.question_type import QuestionType


class TranslationError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class Translator:
    def __init__(self, json_string: str) -> None:
        self._json_string = json_string

    @staticmethod
    def get_responder_uri(json_string: str) -> str:
        json_form = json.loads(json_string)
        return json_form['responderUri']

    @staticmethod
    def get_form_title(json_string: str) -> str:
        json_form = json.loads(json_string)
        return json_form['info']['title']  # TODO

    @staticmethod
    def may_have_options(task_type_name: str):
        types_that_may_have = {
            QuestionType.ONE_CHOICE.name,
            QuestionType.MULTIPLE_CHOICE.name,
        }
        return task_type_name in types_that_may_have

    def translate(self) -> list[dict]:
        my_json: dict = json.loads(self._json_string)
        tasks: list[dict] = []
        for pair in enumerate(my_json['items']):
            tasks.append(self._translate_item(*pair))
        return tasks

    def _translate_item(self, ind: int, item: dict) -> dict:
        if 'title' not in item:
            raise TranslationError(f'question №{ind}: cannot parse question without title')
        if 'questionItem' not in item:
            raise TranslationError(
                f'question №{ind} - <i>{item["title"]}</i>: cannot parse that type of questions')  # todo for matrix question and maybe others

        translated = {
            "google_form_question_id": self._get_google_form_question_id(item),
            "text": self._get_text(item),
            "description": self._get_description(item),
            "required": self._get_required(item),
            "input_media": self._get_input_media(item),
            "task_type": self._get_task_type(item),
        }

        if Translator.may_have_options(translated["task_type"]):
            options, is_other = self._get_options_and_is_other(item)
            if options:
                translated["options"] = options
                translated["is_other"] = is_other

        return translated

    @staticmethod
    def _get_google_form_question_id(item: dict) -> str:
        try:
            return item['questionItem']['question']['questionId']
        except KeyError:
            raise TranslationError(f'cannot parse question: {item["title"]}')

    @staticmethod
    def _get_text(item: dict) -> str:
        if 'title' not in item:
            raise TranslationError(f'cannot parse question: {item["title"]}')

        return item['title']

    @staticmethod
    def _get_description(item: dict) -> str:
        return item['description'] if 'description' in item else None

    @staticmethod
    def _get_required(item: dict) -> bool:
        try:
            return item['questionItem']['question']['required']
        except KeyError:
            return False

    @staticmethod
    def _get_input_media(item: dict) -> str | None:
        if 'image' not in item['questionItem']:
            return None
        return item['questionItem']['image']['contentUri']

    @staticmethod
    def _get_task_type(item: dict) -> str:
        if 'textQuestion' in item['questionItem']['question']:
            return QuestionType.STRING_OR_TEXT.name

        elif 'choiceQuestion' in item['questionItem']['question']:
            try:
                type_ = item['questionItem']['question']['choiceQuestion']['type']
            except KeyError:
                raise TranslationError(f'cannot parse question type: {item["title"]}')

            if type_ == "RADIO":
                return QuestionType.ONE_CHOICE.name
            elif type_ == "CHECKBOX":
                return QuestionType.MULTIPLE_CHOICE.name

        # todo add other types here
        raise TranslationError(f'cannot parse question type: {item["title"]}')

    @staticmethod
    def _get_options_and_is_other(item: dict):
        try:
            options_dict = item['questionItem']['question']['choiceQuestion']['options']
            options = []
            is_other = False
            for value_dict in options_dict:
                if "value" in value_dict:
                    options.append(value_dict["value"])
                elif "isOther" in value_dict:
                    is_other = True
                else:
                    raise TranslationError(f'cannot parse question: {item["title"]}')

            return options, is_other

        except KeyError:
            return None, False
