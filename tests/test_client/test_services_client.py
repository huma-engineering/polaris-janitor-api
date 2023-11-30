import os
from typing import Dict, List

import httpx
import pytest
from mock import Mock
from pytest_mock import MockFixture
from respx import MockRouter

from dhos_janitor_api.blueprint_api import ClientRepository
from dhos_janitor_api.blueprint_api.client import services_client


@pytest.mark.usefixtures("mock_system_jwt", "mock_clinician_jwt")
@pytest.mark.respx(base_url=os.getenv("GDM_BFF"))
class TestServicesClient:
    @pytest.fixture
    def spy_make_request(self, mocker: MockFixture) -> Mock:
        return mocker.spy(services_client, "make_request")

    def test_search_patients(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        system_jwt: str,
        spy_make_request: Mock,
    ) -> None:
        mock_search_patients = respx_mock.get(
            url="/gdm/v1/internal/patient/search"
        ).mock(
            return_value=httpx.Response(
                status_code=200,
                json=[{}],
            )
        )

        actual = services_client.search_patients(clients, system_jwt, "GDM")
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="get",
            url="/gdm/v1/internal/patient/search",
            params={"product_name": "GDM", "active": True},
            headers={"Authorization": f"Bearer {system_jwt}"},
        )

        assert mock_search_patients.called
        assert isinstance(actual, List)

    def test_get_patients_at_location(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        system_jwt: str,
        spy_make_request: Mock,
    ) -> None:
        location_id = "123"
        mock_get_patients_at_location = respx_mock.get(
            url=f"/gdm/v2/internal/location/{location_id}/patient?product_name=GDM&active=true"
        ).mock(
            return_value=httpx.Response(
                status_code=200,
                json=[{}],
            )
        )

        actual = services_client.get_patients_at_location(
            clients, location_id, "GDM", system_jwt
        )
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="get",
            url=f"/gdm/v2/internal/location/{location_id}/patient",
            params={"product_name": "GDM", "active": True},
            headers={"Authorization": f"Bearer {system_jwt}"},
        )

        assert mock_get_patients_at_location.called
        assert isinstance(actual, List)

    def test_create_patient(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        spy_make_request: Mock,
        clinician_jwt: str,
    ) -> None:
        mock_create_patient = respx_mock.post(url="/gdm/v1/internal/patient").mock(
            return_value=httpx.Response(
                status_code=200,
                json={},
            )
        )

        actual = services_client.create_patient(clients, {}, "GDM", clinician_jwt)
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="post",
            url="/gdm/v1/internal/patient",
            params={"product_name": "GDM"},
            json={},
            headers={"Authorization": f"Bearer {clinician_jwt}"},
        )

        assert mock_create_patient.called
        assert isinstance(actual, Dict)

    def test_update_patient(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        system_jwt: str,
        spy_make_request: Mock,
    ) -> None:
        patient_id = "123"
        mock_update_patient = respx_mock.patch(
            url=f"/gdm/v1/patient/{patient_id}"
        ).mock(
            return_value=httpx.Response(
                status_code=200,
            )
        )

        services_client.update_patient(clients, patient_id, {}, system_jwt)
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="patch",
            url=f"/gdm/v1/patient/{patient_id}",
            json={},
            headers={"Authorization": f"Bearer {system_jwt}"},
        )

        assert mock_update_patient.called
