from typing import Dict

from dhos_janitor_api.blueprint_api import ClientRepository
from dhos_janitor_api.blueprint_api.client.common import make_request


def create_activation_for_patient(
    clients: ClientRepository, patient_id: str, system_jwt: str
) -> Dict:
    response = make_request(
        client=clients.gdm_bff,
        method="post",
        url=f"/gdm/v1/internal/patient/{patient_id}/activation",
        headers={"Authorization": f"Bearer {system_jwt}"},
    )
    return response.json()


def create_activation_for_device(
    clients: ClientRepository, device_id: str, system_jwt: str
) -> Dict:
    response = make_request(
        client=clients.gdm_bff,
        method="post",
        url=f"/gdm/v1/internal/device/{device_id}/activation",
        headers={"Authorization": f"Bearer {system_jwt}"},
    )
    return response.json()


def create_device(
    clients: ClientRepository,
    device_id: str,
    location_id: str,
    system_jwt: str,
) -> Dict:
    response = make_request(
        client=clients.gdm_bff,
        method="post",
        url=f"/gdm/v1/internal/device",
        json={
            "uuid": device_id,
            "location_id": location_id,
            "description": f"static device {device_id}",
        },
        headers={"Authorization": f"Bearer {system_jwt}"},
    )
    return response.json()


def create_activation(
    clients: ClientRepository, activation_code: str, otp: str
) -> Dict:
    response = make_request(
        client=clients.gdm_bff,
        method="post",
        url=f"/gdm/v1/activation/{activation_code}",
        json={"otp": otp},
    )
    return response.json()


def get_patient_jwt(
    clients: ClientRepository, patient_id: str, authorisation_code: str
) -> Dict:
    response = make_request(
        client=clients.gdm_bff,
        method="get",
        url=f"/gdm/v1/patient/{patient_id}/jwt",
        headers={"x-authorisation-code": authorisation_code},
    )
    return response.json()
