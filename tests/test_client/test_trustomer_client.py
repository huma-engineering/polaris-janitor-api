import os
from typing import Dict

import httpx
import pytest
from mock import Mock
from pytest_mock import MockFixture
from respx import MockRouter

from dhos_janitor_api.blueprint_api.client import ClientRepository, trustomer_client


@pytest.mark.respx(base_url=os.getenv("GDM_BFF"))
class TestTrustomerClient:
    @pytest.fixture
    def spy_make_request(self, mocker: MockFixture) -> Mock:
        return mocker.spy(trustomer_client, "make_request")

    def test_get_trustomer_config(
        self, clients: ClientRepository, respx_mock: MockRouter, spy_make_request: Mock
    ) -> None:
        config = {"some": "config"}
        mocked_route = respx_mock.get("/gdm/v1/trustomer/test").mock(
            return_value=httpx.Response(status_code=200, json=config)
        )
        trustomer_config = trustomer_client.get_trustomer_config(clients=clients, system_jwt="secret")
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="get",
            url="/gdm/v1/trustomer/test",
            headers={"Authorization": "Bearer secret"},
        )
        assert mocked_route.called
        assert trustomer_config == config

    def test_get_trustomer_config_cached(
        self, clients: ClientRepository, respx_mock: MockRouter, spy_make_request: Mock
    ) -> None:
        config = {"some": "config"}
        mocked_route = respx_mock.get("/gdm/v1/trustomer/test").mock(
            return_value=httpx.Response(status_code=200, json=config)
        )
        trustomer_config = trustomer_client.get_trustomer_config(clients=clients, system_jwt="secret")
        spy_make_request.assert_called_once()
        assert mocked_route.call_count == 1
        assert trustomer_config == config

        trustomer_config = trustomer_client.get_trustomer_config(clients=clients, system_jwt="secret")
        spy_make_request.assert_called_once()
        assert mocked_route.call_count == 1
        assert trustomer_config == config

    def test_get_trustomer_config_stale_cache(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        trustomer_dummy_config: Dict,
        spy_make_request: Mock,
    ) -> None:
        config = {"some": "config"}
        mocked_route = respx_mock.get("/gdm/v1/trustomer/test").mock(
            return_value=httpx.Response(status_code=200, json=config)
        )
        trustomer_config = trustomer_client.get_trustomer_config(clients=clients, system_jwt="secret")
        assert spy_make_request.call_count == 1
        assert mocked_route.call_count == 1
        assert trustomer_config == config

        # unfortunately `freezegun` doesn't work here as TTLCache's
        #   time.monotonic is instantiated before freezegun's freeze.
        trustomer_client._cache.clear()
        trustomer_config = trustomer_client.get_trustomer_config(clients=clients, system_jwt="secret")

        assert spy_make_request.call_count == 2
        assert mocked_route.call_count == 2
        assert trustomer_config == config
