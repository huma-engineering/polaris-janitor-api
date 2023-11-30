import os
from typing import List

import httpx
import pytest
from mock import Mock
from pytest_mock import MockFixture
from respx import MockRouter

from dhos_janitor_api.blueprint_api.client import ClientRepository, medication_client


@pytest.mark.usefixtures("mock_system_jwt")
@pytest.mark.respx(base_url=os.getenv("GDM_BFF"))
class TestMedicationClient:
    @pytest.fixture
    def spy_make_request(self, mocker: MockFixture) -> Mock:
        return mocker.spy(medication_client, "make_request")

    def test_get_medications(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        spy_make_request: Mock,
    ) -> None:
        mock_get_medications = respx_mock.get(url="/gdm/v1/medication").mock(
            return_value=httpx.Response(
                status_code=200,
                json=[
                    {"name": "location", "sct_code": 123, "unit": "mmol", "uuid": "123"}
                ],
            )
        )

        medication_client.get_medications(
            clients=clients, medication_tag="gdm-uk-default"
        )
        actual = medication_client.get_medications(
            clients=clients, medication_tag="gdm-uk-default"
        )
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="get",
            url="/gdm/v1/medication",
            headers={
                "Authorization": "secret",
                "X-Trustomer": "test",
                "X-Product": "gdm",
            },
            params={"tag": "gdm-uk-default"},
        )

        assert mock_get_medications.call_count == 1
        assert isinstance(actual, List)
