import asyncio
import json
from typing import Any

from src.examobot.form_handlers.exceptions import *
import requests
from lxml import html


class FormAnswerSender:
    """
    Class for sending answers to Google Forms.
    Basically, just use send_answer_... for sending answer.
    """
    @staticmethod
    def _create_send_url(base_url: str, answers: dict[int, str]) -> str:
        """
        This function creates needed link that when accessing allows to fill the form.
        :param base_url: Responder URI link for viewing form.
        :param answers: Dictionary where keys are numbers of question items in dec format and values are the answers.
        :return: URL link that will fill the form if sending request to it.
        :raises URLFailedCreationError: error that indicates that there was a problem during creating needed link.
        """
        try:
            form_id = base_url.split("/")[-2]
            new_url = f'https://docs.google.com/forms/d/e/{form_id}/formResponse?&submit=Submit?&'
            for entry_id, answer in answers.items():
                entry_param = f'entry.{entry_id}={answer}&'
                new_url += entry_param
            return new_url
        except Exception as e:
            raise URLFailedCreationError from e

    @staticmethod
    def _determine_if_test_is_complete(html_str: str):
        """
        This function determines if the test was completed after sending request to the forms link.
        :param html_str: String representation of html page after sending answer to Google Forms. It could be either
        the page that is telling that form is complete or the page with marks on what was wrong with previous
        answers.
        :raises HTMLParseError: error that indicates that `html_str` is probably in the wrong format.
        :raises TestCompleteFailError: error that indicates that `html_str` had forms inside thus sending answers
        definitely failed.
        """
        try:
            # Parse the HTML string
            tree = html.fromstring(html_str)

            # Check if the page contains a form tag
            form_tags = tree.xpath('//form')
        except Exception as e:
            raise HTMLParseError(html_str) from e
        if form_tags:
            raise TestCompleteFailError()

    @staticmethod
    async def send_answer_metadata(metadata: str, answers: dict[int, str]):
        """
        Sends given `answers` to the needed form from `metadata`.
        :param metadata: Metadata of Forms in JSON string format.
        :param answers: Dictionary where keys are numbers of question items in dec format and values are the answers.
        """
        data = FormAnswerSender._parse_json(metadata)
        await FormAnswerSender.send_answer_data(data, answers)

    @staticmethod
    async def send_answer_data(data: dict[str, Any], answers: dict[int, str]):
        """
        Sends given `answers` to the needed form from `data`.
        :param data: Data of Forms in dictionary format.
        :param answers: Dictionary where keys are numbers of question items in dec format and values are the answers.
        """
        await FormAnswerSender.send_answer_responder_uri(data["responderUri"], answers)

    @staticmethod
    async def send_answer_responder_uri(responder_uri: str, answers: dict[int, str]):
        """
        Sends given `answers` to the given `responder_uri`.
        :param responder_uri: link for viewing form.
        :param answers: Dictionary where keys are numbers of question items in dec format and values are the answers.
        """
        url = FormAnswerSender._create_send_url(responder_uri, answers)
        resp = requests.get(url)
        FormAnswerSender._raise_for_status_custom_exception(resp, url)
        FormAnswerSender._determine_if_test_is_complete(resp.text)

    @staticmethod
    def _raise_for_status_custom_exception(resp, url):
        """
        Raises :class:`BadRequestError`, if one occurred.
        :param resp: Response after sending request to fill the form.
        :param url: URL to which the request was sent.
        """
        try:
            print(resp.status_code)
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise BadRequestError(url) from e

    @staticmethod
    def _parse_json(metadata):
        """
        Raises :class:`BadRequestError`, if one occurred.
        :param metadata: Metadata of Forms in JSON string format.
        :returns: Data of Forms in dictionary format.
        """
        try:
            return json.loads(metadata)
        except Exception as e:
            raise JSONParseError(metadata) from e


def _correct_send(form_answer_sender, data):
    correct_answers = {
        1868536814: "1965",
        1059122755: "%D0%91%D0%B5%D0%B1%D1%80%D0%B0",
        748499805: "%D0%91%D0%B8%D0%B1%D0%B0",
        857106950: "%D0%92%D0%B0%D1%80%D0%B8%D0%B0%D0%BD%D1%82+1",
        422932123: "%D0%92%D0%B0%D1%80%D0%B8%D0%B0%D0%BD%D1%82+1"
    }
    asyncio.run(form_answer_sender.send_answer_data(data, correct_answers))


def _incorrect_send_fail(form_answer_sender, data):
    incorrect_answers = {
        1868536814: "1965",
        10522755: "%D0%91%D0%B5%D0%B1%D1%80%D0%B0",
        748499805: "%D0%91%D0%B8%D0%B1%D0%B0",
        857106950: "%D0%92%D0%B0%D1%80%D0%B8%D0%B0%D0%BD%D1%82+1",
        422932123: "%D0%92%D0%B0%D1%80%D0%B8%D0%B0%D0%BD%D1%82+1"
    }
    try:
        asyncio.run(form_answer_sender.send_answer_data(data, incorrect_answers))
    except TestCompleteFailError as e:
        print(e)
        print("If this error was caught then we successfully sent answers but they were in a wrong format.")


def main():
    form_answer_sender = FormAnswerSender()
    print(help(form_answer_sender))
    with open("examples/exampleForm.json", 'r') as file:
        data = json.load(file)
    _correct_send(form_answer_sender, data)
    _incorrect_send_fail(form_answer_sender, data)


if __name__ == "__main__":
    main()
