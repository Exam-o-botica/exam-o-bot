import json
from enum import Enum

from examobot.definitions import *


class Phrase(Enum):
    START = "phrase_start"


class LocalizedInterface:
    def __init__(self) -> None:
        self.__language = DEFAULT_LANGUAGE
        self.__mappings = {
            DEFAULT_LANGUAGE: self.__parse_json(DEFAULT_LOCALIZATION_FILE_NAME)
        }

    def __parse_json(self, json_name: str) -> dict[str, str]:
        with open(LOCALIZATIONS_DIR.join(json_name)) as mapping_file:
            return json.load(mapping_file)

    def __load_language(self, language: SupportedLanguages) -> None:
        if language and language not in self.__mappings:
            json_name = language.value.lower() + ".json"
            self.__mappings[language] = self.__parse_json(json_name)

    def get_phrase(self, phrase: Phrase, language: SupportedLanguages = DEFAULT_LANGUAGE) -> str:
        self.__load_language(language)
        return self.__mappings[language][phrase.value]
