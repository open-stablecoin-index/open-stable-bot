import json
from datetime import timedelta

import pytest
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone
from django.urls import reverse


# Run all tests including noisy ones:
# pytest --run-noisy
# Run the tests with the noisy marker:
# pytest -m noisy
# Running all tests without noisy tests:
# pytest
def pytest_addoption(parser):
    parser.addoption(
        "--run-noisy", action="store_true", default=False, help="Run noisy tests"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-noisy"):
        # --run-noisy given in cli: do not skip noisy tests
        return
    skip_noisy = pytest.mark.skip(reason="need --run-noisy option to run")
    for item in items:
        if "noisy" in item.keywords:
            item.add_marker(skip_noisy)


def pytest_configure():
    settings.QUIET_MODE = True


@pytest.fixture(scope="function")
def db_access_without_transactions(db):
    """Fixture to allow DB access without transactions."""
    pass


@pytest.fixture(scope="module")
def payload(request):
    if isinstance(request.param, list):
        return_files = {}
        for filename in request.param:
            with open(f"tests/payloads/{filename}.json", "r") as file:
                return_files[filename] = json.load(file)
        return return_files
    else:
        with open(f"tests/payloads/{request.param}.json", "r") as file:
            return json.load(file)


def update_callback_data(payload, new_id):
    # Extract the 'data' field which contains the JSON string
    data_json = payload["callback_query"]["data"]

    # Parse the JSON string into a Python dictionary
    data_dict = json.loads(data_json)

    # Update the 'id' in the dictionary
    data_dict["id"] = new_id

    # Serialize the dictionary back into a JSON string
    payload["callback_query"]["data"] = json.dumps(data_dict)

    return payload
