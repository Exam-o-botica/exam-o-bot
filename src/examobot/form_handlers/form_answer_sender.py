import asyncio
import json
from typing import Any

from src.examobot.form_handlers.exceptions import *
import requests
from lxml import html


class FormAnswerSender:
    @staticmethod
    def _create_send_url(data: dict[str, Any], answers: dict[int, str]) -> str:
        try:
            base_url = data["responderUri"]
            form_id = base_url.split("/")[-2]
            new_url = f'https://docs.google.com/forms/d/e/{form_id}/formResponse?&submit=Submit?&'
            for entry_id, answer in answers.items():
                entry_param = f'entry.{entry_id}={answer}&'
                new_url += entry_param
            return new_url
        except Exception as e:
            raise URLError from e

    @staticmethod
    def _determine_if_test_is_complete(html_str: str):
        try:
            # Parse the HTML string
            tree = html.fromstring(html_str)

            # Check if the page contains a form tag
            form_tags = tree.xpath('//form')
        except Exception as e:
            raise HTMLError(html_str) from e
        if form_tags:
            raise TestCompleteFailError()

    @staticmethod
    async def send_answer_raw(metadata: str, answers: dict[int, str]):
        data = FormAnswerSender._parse_json(metadata)
        await FormAnswerSender.send_answer(data, answers)

    @staticmethod
    async def send_answer(data: dict[str, Any], answers: dict[int, str]):
        url = FormAnswerSender._create_send_url(data, answers)
        resp = requests.get(url)
        FormAnswerSender._raise_for_status_custom_exception(resp, url)
        FormAnswerSender._determine_if_test_is_complete(resp.text)

    @staticmethod
    def _raise_for_status_custom_exception(resp, url):
        try:
            print(resp.status_code)
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise HTTPError(url) from e

    @staticmethod
    def _parse_json(metadata):
        try:
            json.loads(metadata)
        except Exception as e:
            raise JSONParseError(metadata) from e


def correct_send(form_answer_sender, data):
    correct_answers = {
        1868536814: "1965",
        1059122755: "%D0%91%D0%B5%D0%B1%D1%80%D0%B0",
        748499805: "%D0%91%D0%B8%D0%B1%D0%B0",
        857106950: "%D0%92%D0%B0%D1%80%D0%B8%D0%B0%D0%BD%D1%82+1",
        422932123: "%D0%92%D0%B0%D1%80%D0%B8%D0%B0%D0%BD%D1%82+1"
    }
    asyncio.run(form_answer_sender.send_answer(data, correct_answers))


def incorrect_send_fail(form_answer_sender, data):
    incorrect_answers = {
        1868536814: "1965",
        10522755: "%D0%91%D0%B5%D0%B1%D1%80%D0%B0",
        748499805: "%D0%91%D0%B8%D0%B1%D0%B0",
        857106950: "%D0%92%D0%B0%D1%80%D0%B8%D0%B0%D0%BD%D1%82+1",
        422932123: "%D0%92%D0%B0%D1%80%D0%B8%D0%B0%D0%BD%D1%82+1"
    }
    try:
        asyncio.run(form_answer_sender.send_answer(data, incorrect_answers))
    except TestCompleteFailError as e:
        print(e)
        print("If this error was caught then we successfully sent answers but they were in a wrong format.")


def main():
    form_answer_sender = FormAnswerSender()
    with open("examples/exampleForm.json", 'r') as file:
        data = json.load(file)
    correct_send(form_answer_sender, data)
    incorrect_send_fail(form_answer_sender, data)


if __name__ == "__main__":
    main()
