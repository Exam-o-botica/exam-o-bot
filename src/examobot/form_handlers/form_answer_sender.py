import json
from typing import Any

import requests
from googleapiclient import errors


class FormAnswerSender:
    @staticmethod
    def _create_send_url(data: dict[str, Any], answers: dict[int, str]) -> str:
        base_url = data["responderUri"]
        form_id = base_url.split("/")[-2]
        new_url = f'https://docs.google.com/forms/d/e/{form_id}/formResponse?&submit=Submit?'
        for entry_id, answer in answers.items():
            entry_param = f'entry.{entry_id}={answer}&'
            new_url += entry_param
        return new_url

    @staticmethod
    def _determine_if_test_is_complete(answer_page: str) -> bool:
        pass

    @staticmethod
    async def send_answer(metadata: str, answers: dict[int, str]) -> bool:
        try:
            data = json.loads(metadata)
            url = FormAnswerSender._create_send_url(data, answers)
            resp = requests.get(url)
            resp.raise_for_status()
            return FormAnswerSender._determine_if_test_is_complete(resp.text)
        except (errors.HttpError,):
            return False
