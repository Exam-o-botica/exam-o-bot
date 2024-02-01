import json

from src.examobot.db.tables import Task
from src.examobot.task_extractor.questions_classes import QuestionType


class ParsingError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


def get_google_form_question_id(item: dict) -> str:
    if 'questionItem' not in item:
        raise ParsingError(f'cannot parse question: {item["title"]}')

    return item['questionItem']['question']['questionId']


def get_text(item: dict) -> str:
    if 'title' not in item:
        raise ParsingError(f'cannot parse question: {item["title"]}')

    return item['title']


def get_description(item: dict) -> str:
    return item['description'] if 'description' in item else None


def get_required(item: dict) -> bool:
    try:
        return item['questionItem']['question']['required']
    except KeyError:
        return False


def get_input_media(item: dict) -> str | None:
    if 'image' not in item['questionItem']:
        return None
    return item['questionItem']['image']['contentUri']


def get_task_type(item: dict) -> str:
    if 'textQuestion' in item['questionItem']['question']:
        return QuestionType.STRING_OR_TEXT.name

    # todo add other types here
    raise ParsingError(f'cannot parse question: {item["title"]}')


def get_responder_uri(json_string: str) -> str:
    json_form = json.loads(json_string)
    return json_form['responderUri']


def extract_item(item: dict, test_id: int) -> Task:
    if 'questionItem' not in item:
        raise ParsingError(f'cannot parse question: {item["title"]}')  # todo for matrix question and maybe others

    google_form_question_id = get_google_form_question_id(item)
    text = get_text(item)
    description = get_description(item)
    required = get_required(item)
    input_media = get_input_media(item)
    task_type = get_task_type(item)
    test_id = test_id
    return Task(
        google_form_question_id=google_form_question_id,
        text=text,
        description=description,
        required=required,
        input_media=input_media,
        task_type=task_type,
        test_id=test_id
    )


def extract(json_string: str, test_id: int) -> None:
    """
    Casts JSON of an extracted form to the DB representation of tasks and saves them into the DB.
    :param json_string: JSON-representation of a form.
    :param test_id: ID of the test corresponding to the form.
    :return:
    """
    my_json: dict = json.loads(json_string)
    tasks = [
        extract_item(json_item, test_id) for json_item in my_json
    ]

    # todo add all tasks to db here if all tasks were correctly parsed
