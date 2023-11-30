import os
from typing import Dict

import httpx
import pytest
from mock import Mock
from pytest_mock import MockFixture
from respx import MockRouter

from dhos_janitor_api.blueprint_api import ClientRepository
from dhos_janitor_api.blueprint_api.client import telemetry_client


@pytest.mark.usefixtures("mock_patient_jwt", "mock_clinician_jwt")
@pytest.mark.respx(base_url=os.getenv("GDM_BFF"))
class TestTelemetryClient:
    @pytest.fixture
    def spy_make_request(self, mocker: MockFixture) -> Mock:
        return mocker.spy(telemetry_client, "make_request")

    def test_create_patient_installation(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        spy_make_request: Mock,
        patient_id: str,
        patient_jwt: str,
    ) -> None:
        mock_create_patient_installation = respx_mock.post(
            url=f"/gdm/v1/patient/{patient_id}/installation"
        ).mock(
            return_value=httpx.Response(
                status_code=200,
                json={},
            )
        )

        actual = telemetry_client.create_patient_installation(
            clients, patient_id, {}, patient_jwt
        )
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="post",
            url=f"/gdm/v1/patient/{patient_id}/installation",
            json={},
            headers={"Authorization": f"Bearer {patient_jwt}"},
        )

        assert mock_create_patient_installation.called
        assert isinstance(actual, Dict)

    def test_create_clinician_installation(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        spy_make_request: Mock,
        clinician_jwt: str,
    ) -> None:
        clinician_id = "123"
        mock_create_clinician_installation = respx_mock.post(
            url=f"/gdm/v1/clinician/{clinician_id}/installation"
        ).mock(
            return_value=httpx.Response(
                status_code=200,
                json={},
            )
        )

        actual = telemetry_client.create_clinician_installation(
            clients, clinician_id, {}, clinician_jwt
        )
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="post",
            url=f"/gdm/v1/clinician/{clinician_id}/installation",
            json={},
            headers={"Authorization": f"Bearer {clinician_jwt}"},
        )

        assert mock_create_clinician_installation.called
        assert isinstance(actual, Dict)
