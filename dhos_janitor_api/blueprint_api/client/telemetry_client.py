from typing import Dict

from dhos_janitor_api.blueprint_api import ClientRepository
from dhos_janitor_api.blueprint_api.client.common import make_request


def create_patient_installation(
    clients: ClientRepository, patient_id: str, installation: Dict, patient_jwt: str
) -> Dict:
    response = make_request(
        client=clients.gdm_bff,
        method="post",
        url=f"/gdm/v1/patient/{patient_id}/installation",
        json=installation,
        headers={"Authorization": f"Bearer {patient_jwt}"},
    )
    return response.json()


def create_clinician_installation(
    clients: ClientRepository, clinician_id: str, installation: Dict, clinician_jwt: str
) -> Dict:
    response = make_request(
        client=clients.gdm_bff,
        method="post",
        url=f"/gdm/v1/clinician/{clinician_id}/installation",
        json=installation,
        headers={"Authorization": f"Bearer {clinician_jwt}"},
    )
    return response.json()
