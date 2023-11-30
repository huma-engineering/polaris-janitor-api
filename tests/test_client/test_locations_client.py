import os
from typing import Dict

import httpx
import pytest
from mock import Mock
from pytest_mock import MockFixture
from respx import MockRouter

from dhos_janitor_api.blueprint_api import ClientRepository
from dhos_janitor_api.blueprint_api.client import locations_client


@pytest.mark.usefixtures("mock_system_jwt")
@pytest.mark.respx(base_url=os.getenv("GDM_BFF"))
class TestLocationsClient:
    @pytest.fixture
    def spy_make_request(self, mocker: MockFixture) -> Mock:
        return mocker.spy(locations_client, "make_request")

    def test_get_all_locations(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        system_jwt: str,
        spy_make_request: Mock,
    ) -> None:
        mock_get_all_locations = respx_mock.get(
            url="/gdm/v1/internal/location/search"
        ).mock(
            return_value=httpx.Response(
                status_code=200,
                json={},
            )
        )

        actual = locations_client.get_all_locations(
            clients, ["GDM", "DBM", "SEND"], system_jwt
        )
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="get",
            url="/gdm/v1/internal/location/search",
            params={"product_name": ["GDM", "DBM", "SEND"], "compact": True},
            headers={"Authorization": f"Bearer {system_jwt}"},
        )

        assert mock_get_all_locations.called
        assert isinstance(actual, Dict)

    def test_create_location(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        system_jwt: str,
        spy_make_request: Mock,
    ) -> None:
        mock_create_location = respx_mock.post(url="/gdm/v1/location").mock(
            return_value=httpx.Response(
                status_code=200,
                json={},
            )
        )

        actual = locations_client.create_location(clients, {}, system_jwt)
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="post",
            url="/gdm/v1/location",
            headers={"Authorization": f"Bearer {system_jwt}"},
            json={},
        )

        assert mock_create_location.called
        assert isinstance(actual, Dict)
