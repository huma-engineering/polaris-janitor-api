from typing import Dict

from dhos_janitor_api.blueprint_api import ClientRepository
from dhos_janitor_api.blueprint_api.client.common import make_request


def create_question_type(
    clients: ClientRepository, question_type: Dict, system_jwt: str
) -> Dict:
    response = make_request(
        client=clients.gdm_bff,
        method="post",
        url="/gdm/v1/internal/question_type",
        json=question_type,
        headers={"Authorization": f"Bearer {system_jwt}"},
    )
    return response.json()


def create_question_option_type(
    clients: ClientRepository, question_option_type: Dict, system_jwt: str
) -> Dict:
    response = make_request(
        client=clients.gdm_bff,
        method="post",
        url="/gdm/v1/internal/question_option_type",
        json=question_option_type,
        headers={"Authorization": f"Bearer {system_jwt}"},
    )
    return response.json()


def create_question(clients: ClientRepository, question: Dict, system_jwt: str) -> Dict:
    response = make_request(
        client=clients.gdm_bff,
        method="post",
        url="/gdm/v1/internal/question",
        json=question,
        headers={"Authorization": f"Bearer {system_jwt}"},
    )
    return response.json()
