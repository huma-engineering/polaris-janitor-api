import os
from typing import Dict

import httpx
import pytest
from mock import Mock
from pytest_mock import MockFixture
from respx import MockRouter

from dhos_janitor_api.blueprint_api.client import ClientRepository, questions_client


@pytest.mark.usefixtures("mock_system_jwt")
@pytest.mark.respx(base_url=os.getenv("GDM_BFF"))
class TestQuestionsClient:
    @pytest.fixture
    def spy_make_request(self, mocker: MockFixture) -> Mock:
        return mocker.spy(questions_client, "make_request")

    def test_create_question_type(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        system_jwt: str,
        spy_make_request: Mock,
    ) -> None:
        mock_create_question_type = respx_mock.post(
            url="/gdm/v1/internal/question_type"
        ).mock(
            return_value=httpx.Response(
                status_code=200,
                json={},
            )
        )

        actual = questions_client.create_question_type(clients, {}, system_jwt)
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="post",
            url="/gdm/v1/internal/question_type",
            json={},
            headers={"Authorization": f"Bearer {system_jwt}"},
        )

        assert mock_create_question_type.called
        assert isinstance(actual, Dict)

    def test_create_question_option_type(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        system_jwt: str,
        spy_make_request: Mock,
    ) -> None:
        mock_create_question_option_type = respx_mock.post(
            url="/gdm/v1/internal/question_option_type"
        ).mock(
            return_value=httpx.Response(
                status_code=200,
                json={},
            )
        )

        actual = questions_client.create_question_option_type(clients, {}, system_jwt)
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="post",
            url="/gdm/v1/internal/question_option_type",
            json={},
            headers={"Authorization": f"Bearer {system_jwt}"},
        )

        assert mock_create_question_option_type.called
        assert isinstance(actual, Dict)

    def test_create_question(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        system_jwt: str,
        spy_make_request: Mock,
    ) -> None:
        mock_create_question = respx_mock.post(url="/gdm/v1/internal/question").mock(
            return_value=httpx.Response(
                status_code=200,
                json={},
            )
        )

        actual = questions_client.create_question(clients, {}, system_jwt)
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="post",
            url="/gdm/v1/internal/question",
            json={},
            headers={"Authorization": f"Bearer {system_jwt}"},
        )

        assert mock_create_question.called
        assert isinstance(actual, Dict)
