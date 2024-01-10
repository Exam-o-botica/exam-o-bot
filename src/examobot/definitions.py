import enum
import os
from typing import Optional

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# For logging
LOG_IN_FILE = False
MAIN_LOG_FILE = os.path.join(ROOT_DIR, "../../logs/log.txt")

# For DB
DB_DIR = os.path.join(ROOT_DIR, "../../data")
DEFAULT_DB_FILE = os.path.join(DB_DIR, "examobot_db.db")

# For bot
TOKEN = os.getenv("EXAM_O_BOT_TOKEN")
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; rv:84.0) Gecko/20100101 Firefox/84.0"

# For localization
LANGUAGE = "EN"
DEFAULT_LANGUAGE = "EN"
LOCALIZATIONS_DIR = os.path.join(ROOT_DIR, "../../localizations")
DEFAULT_LOCALIZATION_FILE_NAME = "en.json"


class SupportedLanguages(enum.Enum):
    EN = "en"
    RU = "ru"

    @staticmethod
    def get_language(language: str) -> Optional['SupportedLanguages']:
        for lang in SupportedLanguages:
            if lang.value.lower() == language.lower():
                return lang

        return None
