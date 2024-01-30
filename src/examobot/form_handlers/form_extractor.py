import json
import re
import socket
from typing import Optional, Any

from apiclient import discovery
from googleapiclient import errors
from httplib2 import Http
from oauth2client import client, file, tools

from src.examobot.definitions import GOOGLE_CLIENT_SECRETS

socket.setdefaulttimeout(120)

SCOPES = "https://www.googleapis.com/auth/forms.body.readonly"
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"
store = file.Storage("token.json")


# TODO: 2. Parse every question to message
# TODO: 3. Send answer to GoogleForm


class FormExtractor:
    @staticmethod
    def _login() -> Any:
        try:
            creds = store.get()
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
            e.add_note("Login failure")
            raise

    @staticmethod
    def _get_form_id_from_url(url: str) -> str:
        # Define a regular expression pattern to match the form ID
        pattern = r'/forms/d/([a-zA-Z0-9-_]+)'

        # Use re.search to find the pattern in the URL
        match = re.search(pattern, url)

        # Check if a match is found and return the form ID
        assert match, f"Given URL is incorrect: ${url}"
        form_id = match.group(1)
        return form_id

    @staticmethod
    def _get_json(service: Any, form_url: str) -> dict:
        form_id = "NOT_SET"
        try:
            form_id = FormExtractor._get_form_id_from_url(form_url)
            res_json = service.forms().get(formId=form_id).execute()
            return res_json
        except Exception as e:
            e.add_note(f"Google Forms API Error: get() couldn't find the needed id of form: {form_id}")
            raise

    @staticmethod
    async def extract(form_url: str) -> Optional[str]:
        try:
            service = FormExtractor._login()
            res = FormExtractor._get_json(service, form_url)
            return json.dumps(res, ensure_ascii=False, indent=4)
        except (errors.HttpError,):
            return None
