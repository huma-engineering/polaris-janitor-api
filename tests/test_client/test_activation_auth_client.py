import os
from typing import Dict

import httpx
import pytest
from mock import Mock
from pytest_mock import MockFixture
from respx import MockRouter

from dhos_janitor_api.blueprint_api import ClientRepository
from dhos_janitor_api.blueprint_api.client import activation_auth_client


@pytest.mark.usefixtures("mock_system_jwt")
@pytest.mark.respx(base_url=os.getenv("GDM_BFF"))
class TestActivationAuthClient:
    @pytest.fixture
    def spy_make_request(self, mocker: MockFixture) -> Mock:
        return mocker.spy(activation_auth_client, "make_request")

    def test_create_activation_for_patient(
        self,
        clients: ClientRepository,
        patient_id: str,
        respx_mock: MockRouter,
        system_jwt: str,
        spy_make_request: Mock,
    ) -> None:
        mock_create_activation_post = respx_mock.post(
            url=f"/gdm/v1/internal/patient/{patient_id}/activation"
        ).mock(
            return_value=httpx.Response(
                status_code=200,
                json={},
            )
        )

        actual = activation_auth_client.create_activation_for_patient(
            clients, patient_id, system_jwt
        )
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="post",
            url=f"/gdm/v1/internal/patient/{patient_id}/activation",
            headers={"Authorization": f"Bearer {system_jwt}"},
        )

        assert mock_create_activation_post.called
        assert isinstance(actual, Dict)

    def test_create_activation_for_device(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        system_jwt: str,
        spy_make_request: Mock,
        device_id: str,
    ) -> None:
        mock_create_activation_post = respx_mock.post(
            url=f"/gdm/v1/internal/device/{device_id}/activation"
        ).mock(
            return_value=httpx.Response(
                status_code=200,
                json={},
            )
        )
        actual = activation_auth_client.create_activation_for_device(
            clients, device_id, system_jwt
        )
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="post",
            url=f"/gdm/v1/internal/device/{device_id}/activation",
            headers={"Authorization": f"Bearer {system_jwt}"},
        )

        assert mock_create_activation_post.called
        assert isinstance(actual, Dict)

    def test_create_device(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        system_jwt: str,
        spy_make_request: Mock,
        device_id: str,
        location_id: str,
    ) -> None:
        mock_create_device = respx_mock.post(url="/gdm/v1/internal/device").mock(
            return_value=httpx.Response(
                status_code=200,
                json={},
            )
        )

        actual = activation_auth_client.create_device(
            clients, device_id, location_id, system_jwt
        )
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="post",
            url="/gdm/v1/internal/device",
            json={
                "uuid": device_id,
                "location_id": location_id,
                "description": f"static device {device_id}",
            },
            headers={"Authorization": f"Bearer {system_jwt}"},
        )

        assert mock_create_device.called
        assert isinstance(actual, Dict)

    def test_create_activation(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        system_jwt: str,
        spy_make_request: Mock,
    ) -> None:
        activation_code = "123"
        otp = "321"

        mock_create_activation = respx_mock.post(
            url=f"/gdm/v1/activation/{activation_code}"
        ).mock(
            return_value=httpx.Response(
                status_code=200,
                json={},
            )
        )

        actual = activation_auth_client.create_activation(clients, activation_code, otp)
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="post",
            url=f"/gdm/v1/activation/{activation_code}",
            json={"otp": otp},
        )

        assert mock_create_activation.called
        assert isinstance(actual, Dict)

    def test_get_patient_jwt(
        self,
        clients: ClientRepository,
        respx_mock: MockRouter,
        system_jwt: str,
        spy_make_request: Mock,
        patient_id: str,
    ) -> None:
        authorisation_code = "123"

        mock_get_patient_jwt = respx_mock.get(
            url=f"/gdm/v1/patient/{patient_id}/jwt"
        ).mock(
            return_value=httpx.Response(
                status_code=200,
                json={},
            )
        )

        actual = activation_auth_client.get_patient_jwt(
            clients, patient_id, authorisation_code
        )
        spy_make_request.assert_called_once_with(
            client=clients.gdm_bff,
            method="get",
            url=f"/gdm/v1/patient/{patient_id}/jwt",
            headers={"x-authorisation-code": authorisation_code},
        )

        assert mock_get_patient_jwt.called
        assert isinstance(actual, Dict)
