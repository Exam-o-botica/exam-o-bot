import json
import logging
import sys
from typing import Union

from examobot.definitions import *


class PhraseKeys(enum.Enum):
    HI = "hi_word"

    START = "start_phrase"


class Interface:
    def __init__(self, phrase_mapping: dict[str, str]) -> None:
        self.mapping = phrase_mapping

    def __getitem__(self, item: Union[str, PhraseKeys]):
        pass


class LocalizedInterfaceFactory:
    def __init__(self, language_defined: str):
        self.language_defined = language_defined
        language = SupportedLanguages.get_language(self.language_defined)

        with open(MAIN_LOG_FILE, "a") as log:
            if LOG_IN_FILE:
                logging.basicConfig(level=logging.INFO, stream=log)
            else:
                logging.basicConfig(level=logging.INFO, stream=sys.stdout)

            if not language:
                logging.info(f"Unsupported language defined: {self.language_defined}. "
                             f"Switching to default language: {DEFAULT_LANGUAGE}")
                self.expected_json_name = DEFAULT_LOCALIZATION_FILE_NAME
            else:
                self.expected_json_name = language.value.lower() + ".json"

    def __call__(self) -> Interface:
        with open(LOCALIZATIONS_DIR.join(self.expected_json_name)) as mapping_file:
            data = json.load(mapping_file)
            return Interface(data)


if __name__ == '__main__':
    factory = LocalizedInterfaceFactory("en")
    # interface = factory()
