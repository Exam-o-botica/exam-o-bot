import asyncio
import json
from typing import Any

import requests
from googleapiclient import errors
from lxml import html


# TODO: Change logic of class. It should mostly return nothing and throw custom exceptions so that later on
#  it could be caught and handled properly depending on the exception


class FormAnswerSender:
    @staticmethod
    def _create_send_url(data: dict[str, Any], answers: dict[int, str]) -> str:
        base_url = data["responderUri"]
        form_id = base_url.split("/")[-2]
        new_url = f'https://docs.google.com/forms/d/e/{form_id}/formResponse?&submit=Submit?&'
        for entry_id, answer in answers.items():
            entry_param = f'entry.{entry_id}={answer}&'
            new_url += entry_param
        return new_url

    @staticmethod
    def _determine_if_test_is_complete(html_str: str) -> bool:
        try:
            # Parse the HTML string
            tree = html.fromstring(html_str)

            # Check if the page contains a form tag
            form_tags = tree.xpath('//form')

            if form_tags:
                return False
            else:
                return True
        except Exception as e:
            print(f"Error parsing HTML: {e}")
            return False

    @staticmethod
    async def send_answer(metadata: str, answers: dict[int, str]) -> bool:
        try:
            data = json.loads(metadata)
            url = FormAnswerSender._create_send_url(data, answers)
            resp = requests.get(url)
            resp.raise_for_status()
            return FormAnswerSender._determine_if_test_is_complete(resp.text)
        except (errors.HttpError,):
            pass

    @staticmethod
    async def send_answer_(data: dict[str, Any], answers: dict[int, str]):
        try:
            url = FormAnswerSender._create_send_url(data, answers)
            resp = requests.get(url)
            resp.raise_for_status()
            FormAnswerSender._determine_if_test_is_complete(resp.text)
        except Exception as e:
            raise


def main():
    form_answer_sender = FormAnswerSender()
    with open("examples/exampleForm.json", 'r') as file:
        data = json.load(file)
    answers = {
        1868536814: "1965",
        1059122755: "%D0%91%D0%B5%D0%B1%D1%80%D0%B0",
        748499805: "%D0%91%D0%B8%D0%B1%D0%B0",
        857106950: "%D0%92%D0%B0%D1%80%D0%B8%D0%B0%D0%BD%D1%82+1",
        422932123: "%D0%92%D0%B0%D1%80%D0%B8%D0%B0%D0%BD%D1%82+1"
    }
    print(form_answer_sender.send_answer_(data, answers))


if __name__ == "__main__":
    main()
