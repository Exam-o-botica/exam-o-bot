import json

from src.examobot.task_translator.questions_classes import QuestionType


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
        return json_form['info']['title']

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

        google_form_question_id = self._get_google_form_question_id(item)
        text = self._get_text(item)
        description = self._get_description(item)
        required = self._get_required(item)
        input_media = self._get_input_media(item)
        task_type = self._get_task_type(item)
        return {"google_form_question_id": google_form_question_id, "text": text, "description": description,
                "required": required, "input_media": input_media, "task_type": task_type}

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

        # todo add other types here
        raise TranslationError(f'cannot parse question: {item["title"]}')
