from typing import Any

MAX_LENGTH_STR = 50


class FormAnswerSenderException(Exception):
    pass


def _shorten(data: Any) -> str:
    data_str = str(data)
    length = len(data_str)
    if length < MAX_LENGTH_STR:
        return data_str
    else:
        return data_str[:MAX_LENGTH_STR] + "..."


class JSONParseError(FormAnswerSenderException):
    def __init__(self, metadata):
        self.metadata_text = _shorten(metadata)

    def __str__(self):
        return (f"Error happened when trying to parse json:\n"
                f"{self.metadata_text}")


class URLError(FormAnswerSenderException):
    def __str__(self):
        return f"Error happened when trying to create link for sending form."


class HTMLError(FormAnswerSenderException):
    def __init__(self, html_str):
        self.text = _shorten(html_str)

    def __str__(self):
        return (f"Error occurred when parsing html of the result after sending answer.\n"
                f"The given html to parse: {self.text}")


class TestCompleteFailError(FormAnswerSenderException):
    def __str__(self):
        return f'Sending answers was failed. Please check that you wrote everything correctly according to form.'


class HTTPError(TestCompleteFailError):
    def __init__(self, url: str):
        self.url = url

    def __str__(self):
        return (f"Error happened when trying to send answers to form via link:\n"
                f"{self.url}")
