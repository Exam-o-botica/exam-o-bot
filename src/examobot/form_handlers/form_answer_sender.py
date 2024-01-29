import requests
from googleapiclient import errors


class FormAnswerSender:
    @staticmethod
    def _create_send_url(metadata: str, answers: dict[int, str]) -> str:
        # TODO: Write this method it should get all entry points and connect them with given answers
        pass

    @staticmethod
    def _determine_if_test_is_complete(answer_page: str) -> bool:
        pass

    @staticmethod
    async def send_answer(metadata: str, answers: dict[int, str]) -> bool:
        try:
            url = FormAnswerSender._create_send_url(metadata, answers)
            resp = requests.get(url)
            resp.raise_for_status()
            return FormAnswerSender._determine_if_test_is_complete(resp.text)
        except (errors.HttpError,):
            return False
