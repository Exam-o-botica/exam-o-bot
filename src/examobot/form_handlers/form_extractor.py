import json
import re
import socket
from typing import Optional, Any

from apiclient import discovery
from googleapiclient import errors
from httplib2 import Http
from oauth2client import client, tools

from examobot.definitions import GOOGLE_CLIENT_SECRETS, TOKEN_STORE, SCOPES, DISCOVERY_DOC

socket.setdefaulttimeout(120)


class FormExtractor:
    """
    Class for extracting forms in JSON format using Google Forms API.
    Basically, just use extract_...() function for extracting forms.
    """

    @staticmethod
    def _login() -> Any:
        """
        :return: Object for interacting with Google API. Refer to the documentation for the
            `discovery.build` function for more details on building API services in Python.
        """
        try:
            creds = TOKEN_STORE.get()
            if not creds or creds.invalid:
                flow = client.flow_from_clientsecrets(str(GOOGLE_CLIENT_SECRETS), SCOPES)
                creds = tools.run_flow(flow, TOKEN_STORE)

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
        """
        :param url: Responder URI link for editing form.
        :return: Responder form id.
        """
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
        """
        :param service: Object for interacting with Google API.
        :param form_url: Responder URI link for editing form.
        :return: dict which represents the form.
        """
        form_id = "NOT_SET"
        try:
            form_id = FormExtractor._get_form_id_from_url(form_url)
            res_json = service.forms().get(formId=form_id).execute()
            return res_json
        except Exception as e:
            e.add_note(f"Google Forms API Error: get() couldn't find the needed id of form: {form_id}")
            raise

    @staticmethod
    async def extract_string(form_url: str) -> Optional[str]:
        """
        :param form_url: Responder URI link for editing form.
        :return: JSON string which represents the form.
        """
        try:
            service = FormExtractor._login()
            res = FormExtractor._get_json(service, form_url)
            return json.dumps(res, ensure_ascii=False, indent=4)
        except (errors.HttpError,):
            return None

    @staticmethod
    async def extract_dict(form_url: str) -> Optional[dict]:
        """
        :param form_url: Responder URI link for editing form.
        :return: dict which represents the form.
        """
        try:
            service = FormExtractor._login()
            res = FormExtractor._get_json(service, form_url)
            return res
        except (errors.HttpError,):
            return None


def main():
    form_url = "https://docs.google.com/forms/d/1YSEgy19CzMalinchIuOIQ1mUmPGPy5nFOY54IQxaRYk/edit"
    try:
        service = FormExtractor._login()
        res = FormExtractor._get_json(service, form_url)
        final = json.dumps(res, ensure_ascii=False, indent=4)
    except (errors.HttpError,):
        final = None

    print(final)

    # print(help(FormExtractor()))


if __name__ == "__main__":
    main()
