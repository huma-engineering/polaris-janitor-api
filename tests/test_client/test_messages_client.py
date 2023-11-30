import os
from typing import Dict

import httpx
import pytest
from mock import Mock
from pytest_mock import MockFixture
from respx import MockRouter

from dhos_janitor_api.blueprint_api.client import ClientRepository, messages_client


@pytest.mark.usefixtures("mock_clinician_jwt")
@pytest.mark.respx(base_url=os.getenv("GDM_BFF"))
class TestMessagesClient:
    @pytest.fixture
    def spy_make_request(self, mocker: MockFixture) -> Mock:
        return mocker.spy(messages_client, "make_request")

    def test_create_message(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        spy_make_request: Mock,
        clinician_jwt: str,
    ) -> None:

        mock_create_message = respx_mock.post(url="/gdm/v1/internal/message").mock(
            return_value=httpx.Response(
                status_code=200,
                json={},
            )
        )

        actual = messages_client.create_message(clients, {}, clinician_jwt, {})
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="post",
            url="/gdm/v1/internal/message",
            json={},
            headers={"Authorization": f"Bearer {clinician_jwt}"},
        )

        assert mock_create_message.called
        assert isinstance(actual, Dict)
