import enum
import os
from typing import Optional

from dotenv import load_dotenv
from oauth2client import file

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# For logging
LOG_IN_FILE = False
MAIN_LOG_FILE = os.path.join(ROOT_DIR, "../../logs/log.txt")

# For DB
DB_DIR = os.path.join(ROOT_DIR, "../../data")
DEFAULT_DB_FILE = os.path.join(DB_DIR, "examobot_db.db")
DATABASE_URI = os.environ.get("DATABASE_URI")

# For bot
TOKEN = os.environ.get("EXAM_O_BOT_TOKEN")
BOT_NAME = os.environ.get('BOT_NAME')
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; rv:84.0) Gecko/20100101 Firefox/84.0"

# For Google Script API
FORM_HANDLERS_DIR = os.path.join(ROOT_DIR, "form_handlers")
GOOGLE_CREDENTIALS_DIR = os.path.join(FORM_HANDLERS_DIR, "credentials")
GOOGLE_CLIENT_SECRETS = os.path.join(GOOGLE_CREDENTIALS_DIR, "client_secrets.json")
SCOPES = "https://www.googleapis.com/auth/forms.body.readonly"
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"
TOKEN_STORE_PATH = os.path.join(GOOGLE_CREDENTIALS_DIR, "token.json")
TOKEN_STORE = file.Storage(TOKEN_STORE_PATH)


# For localization
class SupportedLanguages(enum.Enum):
    EN = "en"
    RU = "ru"

    @staticmethod
    def to_enum(language: str) -> Optional['SupportedLanguages']:
        for lang in SupportedLanguages:
            if lang.value.lower() == language.lower():
                return lang

        return None


LANGUAGE = SupportedLanguages.EN
DEFAULT_LANGUAGE = SupportedLanguages.EN
LOCALIZATIONS_DIR = os.path.join(ROOT_DIR, "../../localizations")
DEFAULT_LOCALIZATION_FILE_NAME = "en.json"
