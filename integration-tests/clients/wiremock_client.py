import json
import uuid
from typing import Generator

import requests
from behave import fixture
from behave.runner import Context
from environs import Env

MEDICATIONS_DATA = [
    {
        "created": "2019-11-19T13:43:49.581Z",
        "created_by": "dhos-robot",
        "modified": "2019-11-19T13:43:49.581Z",
        "modified_by": "dhos-robot",
        "name": "Admelog",
        "sct_code": "D0000040",
        "tags": [],
        "unit": "units",
        "uuid": "7f37146a-a958-4536-b10a-960e82a8bef7",
    },
]

env = Env()
expected_trustomer = env.str("CUSTOMER_CODE").lower()


def setup_mocked_apis() -> None:
    mocks = (
        {
            "request": {
                "method": "POST",
                "url": "/dhos-notifications/dhos/v1/email",
            },
            "response": {"status": 200},
        },
        {
            "request": {"method": "POST", "url": "/dhos-audit/drop_data"},
            "response": {
                "status": 200,
                "jsonBody": {"complete": True, "time_taken": "1s"},
            },
        },
        {
            "request": {"method": "POST", "url": "/dhos-audit/dhos/v2/event"},
            "response": {
                "status": 201,
                "headers": {"Location": "/dhos-audit/event/1"},
            },
        },
        {
            "request": {"method": "POST", "url": "/dhos-messages/drop_data"},
            "response": {
                "status": 200,
                "jsonBody": {"complete": True, "time_taken": "1s"},
            },
        },
        {
            "request": {
                "method": "POST",
                "urlPattern": "/dhos-messages/dhos/v1/message(.*)",
            },
            "response": {
                "status": 200,
                "body": json.dumps({"uuid": str(uuid.uuid4())}),
                "headers": {"Content-Type": "application/json"},
            },
        },
        {
            "request": {
                "method": "POST",
                "urlPattern": "/dhos-messages/dhos/v2/message",
            },
            "response": {
                "status": 200,
                "body": json.dumps({"uuid": str(uuid.uuid4())}),
                "headers": {"Content-Type": "application/json"},
            },
        },
        {
            "request": {
                "method": "GET",
                "urlPattern": "/dhos-medications/dhos/v1/medication(.*)",
            },
            "response": {
                "status": 200,
                "body": json.dumps(
                    MEDICATIONS_DATA, allow_nan=False, sort_keys=False, indent=4
                ),
                "headers": {"Content-Type": "application/json"},
            },
        },
        {
            "request": {"method": "POST", "url": "/dhos-telemetry/drop_data"},
            "response": {
                "status": 200,
                "jsonBody": {"complete": True, "time_taken": "1s"},
            },
        },
        {
            "request": {
                "method": "POST",
                "urlPattern": "/dhos-telemetry/dhos/v1/patient/(.*?)/installation",
            },
            "response": {"status": 200, "body": json.dumps({})},
        },
        {
            "request": {
                "method": "POST",
                "urlPattern": "/dhos-telemetry/dhos/v1/clinician/(.*?)/installation",
            },
            "response": {"status": 200, "body": json.dumps({})},
        },
    )
    for payload in mocks:
        response = requests.post("http://wiremock:8080/__admin/mappings", json=payload)
        response.raise_for_status()


def reset_wiremock() -> None:
    response = requests.post("http://wiremock:8080/__admin/reset")
    response.raise_for_status()


@fixture
def mock_apis(context: Context) -> Generator[None, None, None]:
    setup_mocked_apis()
    yield
    reset_wiremock()
