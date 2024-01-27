from pprint import pprint
import socket
import json
import sys

from googleapiclient import errors

from src.login import login

socket.setdefaulttimeout(120)


# Get JSON, which is returned by script
def get_json(service, file_name, script_id, form_url):
    pprint('Exporting form...')
    body = {
        "function": "main",
        "devMode": True,
        "parameters": form_url
    }
    # Get JSON from script
    resp = service.scripts().run(scriptId=script_id, body=body).execute()

    # Write out JSON to file
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(resp['response']['result'], f, ensure_ascii=False, indent=4)

    pprint('Form was successfully exported')


def main():
    try:
        config_file_name = "config.json"
        file_name = "result.json"
        script_id = "1-sriQtifGbmN530Pr3kpsh-VVA5NW7DXJ7pdvsr9tcrBUU6O0QEFjlW0"
        form_url = "docs.google.com/forms/d/1WlvO6r5-7CvkjCvL7y80yhV4UqtFqpgIln-xQmVatas/edit"

        with open(config_file_name, "r") as f:
            config = json.load(f)

        service = login(config)

        get_json(service, file_name, script_id, form_url)

    except (errors.HttpError,) as error:
        # The API encountered a problem.
        pprint(error.content.decode('utf-8'))


if __name__ == '__main__':
    main()
