import os
from typing import Dict, List

import httpx
import pytest
from mock import Mock
from pytest_mock import MockFixture
from respx import MockRouter

from dhos_janitor_api.blueprint_api import ClientRepository
from dhos_janitor_api.blueprint_api.client import users_client


@pytest.mark.usefixtures("mock_system_jwt", "mock_clinician_jwt")
@pytest.mark.respx(base_url=os.getenv("GDM_BFF"))
class TestServicesClient:
    @pytest.fixture
    def spy_make_request(self, mocker: MockFixture) -> Mock:
        return mocker.spy(users_client, "make_request")

    def test_get_clinicians_at_location(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        system_jwt: str,
        spy_make_request: Mock,
    ) -> None:
        location_id = "123"
        mock_get_clinicians_at_location = respx_mock.get(
            url=f"/gdm/v1/location/{location_id}/clinician"
        ).mock(
            return_value=httpx.Response(
                status_code=200,
                json=[{}],
            )
        )

        actual = users_client.get_clinicians_at_location(
            clients, location_id, system_jwt
        )
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="get",
            url=f"/gdm/v1/location/{location_id}/clinician",
            headers={"Authorization": f"Bearer {system_jwt}"},
        )

        assert mock_get_clinicians_at_location.called
        assert isinstance(actual, List)

    def test_get_clinicians(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        system_jwt: str,
        spy_make_request: Mock,
    ) -> None:
        mock_get_clinicians = respx_mock.get(url="/gdm/v2/internal/clinicians").mock(
            return_value=httpx.Response(
                status_code=200,
                json={"results": [{}], "total": 1},
            )
        )

        actual = users_client.get_clinicians(clients, "GDM", system_jwt)
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="get",
            url="/gdm/v2/internal/clinicians",
            params={"product_name": "GDM"},
            headers={"Authorization": f"Bearer {system_jwt}"},
        )

        assert mock_get_clinicians.called
        assert isinstance(actual, List)

    def test_create_clinician(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        system_jwt: str,
        spy_make_request: Mock,
    ) -> None:
        mock_create_clinician = respx_mock.post(url="/gdm/v1/clinician").mock(
            return_value=httpx.Response(status_code=200, json={})
        )

        actual = users_client.create_clinician(clients, {}, system_jwt)
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="post",
            url="/gdm/v1/clinician",
            params={"send_welcome_email": False},
            json={},
            headers={"Authorization": f"Bearer {system_jwt}"},
        )

        assert mock_create_clinician.called
        assert isinstance(actual, Dict)

    def test_update_clinician(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        system_jwt: str,
        spy_make_request: Mock,
    ) -> None:
        mock_update_clinician = respx_mock.patch(url="/gdm/v1/internal/clinician").mock(
            return_value=httpx.Response(status_code=200, json={})
        )

        actual = users_client.update_clinician(
            clients, "gregory@house.doctor", {}, system_jwt
        )
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="patch",
            url="/gdm/v1/internal/clinician",
            params={"email": "gregory@house.doctor"},
            json={},
            headers={"Authorization": f"Bearer {system_jwt}"},
        )

        assert mock_update_clinician.called
        assert isinstance(actual, Dict)
