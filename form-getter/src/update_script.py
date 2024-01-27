from pprint import pprint
import json
import sys

from googleapiclient import errors

from src.login import login

MANIFEST = '''
{
    "timeZone": "Europe/Moscow",
    "dependencies": {
    },
    "exceptionLogging": "STACKDRIVER",
    "executionApi": {
        "access": "ANYONE"
    },
    "runtimeVersion": "V8"
}
'''.strip()


def update_project(service, script_id, script_file_name):
    # Read from file code we want to deploy
    with open(script_file_name, 'r') as f:
        sample_code = f.read()

    # Upload two files to the project
    request = {
        'files': [{
            'name': 'hello',
            'type': 'SERVER_JS',
            'source': sample_code
        }, {
            'name': 'appsscript',
            'type': 'JSON',
            'source': MANIFEST
        }
        ]
    }

    # Update files in the project
    service.projects().updateContent(
        body=request,
        scriptId=script_id
    ).execute()

    pprint('Project was successfully updated')


def main():

    try:
        config_file_name = "config.json"
        script_id = "1-sriQtifGbmN530Pr3kpsh-VVA5NW7DXJ7pdvsr9tcrBUU6O0QEFjlW0"
        script_file_name = "script.gs"

        with open(config_file_name, "r") as f:
            config = json.load(f)

        service = login(config)

        update_project(service, script_id, script_file_name)

    except (errors.HttpError, ) as error:
        # The API encountered a problem.
        pprint(error.content.decode('utf-8'))


if __name__ == '__main__':
    main()