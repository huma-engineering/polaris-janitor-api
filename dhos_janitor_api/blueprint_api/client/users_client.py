from typing import Dict, List

from dhos_janitor_api.blueprint_api import ClientRepository
from dhos_janitor_api.blueprint_api.client.common import make_request


def get_clinicians_at_location(
    clients: ClientRepository, location_uuid: str, system_jwt: str
) -> List[Dict]:
    response = make_request(
        client=clients.dhos_users_api,
        method="get",
        url=f"/dhos/v1/location/{location_uuid}/clinician",
        headers={"Authorization": f"Bearer {system_jwt}"},
    )
    return response.json()


def get_clinicians(
    clients: ClientRepository, product_name: str, system_jwt: str
) -> List[Dict]:
    response = make_request(
        client=clients.dhos_users_api,
        method="get",
        url="/dhos/v2/clinicians",
        headers={"Authorization": f"Bearer {system_jwt}"},
        params={"product_name": product_name},
    )
    data = response.json()
    return data["results"]


def create_clinician(
    clients: ClientRepository, clinician_details: Dict, system_jwt: str
) -> Dict:
    response = make_request(
        client=clients.dhos_users_api,
        method="post",
        url="/dhos/v1/clinician",
        params={"send_welcome_email": False},
        json=clinician_details,
        headers={"Authorization": f"Bearer {system_jwt}"},
    )
    return response.json()


def update_clinician(
    clients: ClientRepository,
    clinician_email: str,
    clinician_details: Dict,
    system_jwt: str,
) -> Dict:
    response = make_request(
        client=clients.dhos_users_api,
        method="patch",
        url="/dhos/v1/clinician",
        params={"email": clinician_email},
        json=clinician_details,
        headers={"Authorization": f"Bearer {system_jwt}"},
    )
    return response.json()
