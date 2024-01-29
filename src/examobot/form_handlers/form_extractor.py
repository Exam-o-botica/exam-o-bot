import json
import re
import socket
from pprint import pprint
from typing import Optional

from apiclient import discovery
from googleapiclient import errors
from httplib2 import Http
from oauth2client import client, file, tools

from src.examobot.definitions import GOOGLE_SCRIPT_ID, GOOGLE_CLIENT_SECRETS

socket.setdefaulttimeout(120)

SCOPES = "https://www.googleapis.com/auth/forms.body.readonly"
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"
store = file.Storage("token.json")


class FormExtractor:
    @staticmethod
    def _login(client_secrets):
        try:
            creds = None
            if not creds or creds.invalid:
                flow = client.flow_from_clientsecrets(str(GOOGLE_CLIENT_SECRETS), SCOPES)
                creds = tools.run_flow(flow, store)

            service = discovery.build(
                "forms",
                "v1",
                http=creds.authorize(Http()),
                discoveryServiceUrl=DISCOVERY_DOC,
                static_discovery=False,
            )
            return service
        except Exception as e:
            pprint(f'Login failure: {e}')
            return None

    @staticmethod
    def _get_form_id_from_url(url: str) -> str | None:
        # Define a regular expression pattern to match the form ID
        pattern = r'/forms/d/([a-zA-Z0-9-_]+)'

        # Use re.search to find the pattern in the URL
        match = re.search(pattern, url)

        # Check if a match is found and return the form ID
        if match:
            form_id = match.group(1)
            return form_id
        else:
            # Return None if no match is found
            return None

    @staticmethod
    def _get_json(service, script_id, form_url):
        try:
            form_id = FormExtractor._get_form_id_from_url(form_url)
            res_json = service.forms().get(formId=form_id).execute()
            return res_json
        except Exception as e:
            pprint(f'Script failure: {e}')
            return None

    # TODO: extract is a public method everything else is private
    @staticmethod
    async def extract(form_url: str) -> Optional[str]:
        try:
            service = FormExtractor._login(None)
            res = FormExtractor._get_json(service, GOOGLE_SCRIPT_ID, form_url)
            return json.dumps(res, ensure_ascii=False, indent=4)
        except (errors.HttpError,):
            return None
