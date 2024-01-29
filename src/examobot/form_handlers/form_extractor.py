import json
import os.path
import pickle
import socket
from pprint import pprint
from typing import Optional

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import errors
from googleapiclient.discovery import build

from src.examobot.definitions import GOOGLE_SCRIPT_ID, GOOGLE_CONFIG_FILE, FORM_HANDLERS_DIR

socket.setdefaulttimeout(120)


class FormExtractor:
    @staticmethod
    def _login(config):
        try:
            creds = None
            token_file = os.path.join(
                FORM_HANDLERS_DIR, config['credentials_path'], config['token_file'])
            credentials_file = os.path.join(
                FORM_HANDLERS_DIR, config['credentials_path'], config['credentials_file'])

            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), config['SCOPES'])
                    creds = flow.run_local_server(port=0)

                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)

            service = build('script', 'v1', credentials=creds)
            pprint('Login successful')
            return service

        except Exception as e:
            pprint(f'Login failure: {e}')
            return None

    @staticmethod
    def _get_json(service, script_id, form_url):
        try:
            body = {
                "function": "main",
                "devMode": True,
                "parameters": form_url
            }
            resp = service.scripts().run(scriptId=script_id, body=body).execute()
            result_json = json.dumps(resp['response']['result'], ensure_ascii=False, indent=4)
            return result_json
        except Exception as e:
            pprint(f'Script failure: {e}')
            return None

    # TODO: extract is a public method everything else is private
    @staticmethod
    async def extract(form_url: str) -> Optional[str]:
        try:
            with open(GOOGLE_CONFIG_FILE, "r") as f:
                config = json.load(f)

            service = FormExtractor._login(config)
            meta_data = FormExtractor._get_json(service, GOOGLE_SCRIPT_ID, form_url)
            return meta_data
        except (errors.HttpError,):
            return None
