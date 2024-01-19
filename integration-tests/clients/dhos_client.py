from typing import Dict, List, Optional

import requests
from behave import use_fixture
from behave.runner import Context
from helpers.security import (
    generate_superclinician_token,
    generate_system_token,
    get_system_token,
)


def database_reset(
    context: Context,
    num_gdm_patients: int,
    num_dbm_patients: int,
    num_send_patients: int,
    num_hospitals: Optional[int] = None,
    num_wards: Optional[int] = None,
) -> None:
    use_fixture(get_system_token, context)

    response = requests.post(
        "http://dhos-janitor-api:5000/dhos/v1/reset_task",
        headers={"Authorization": f"Bearer {context.system_jwt}"},
        params={
            "num_gdm_patients": num_gdm_patients,
            "num_dbm_patients": num_dbm_patients,
            "num_send_patients": num_send_patients,
            "num_hospitals": num_hospitals,
            "num_wards": num_wards,
        },
        timeout=30,
    )
    assert response.status_code == 202, f"{response.status_code} {response.text}"
    task_url = response.headers["Location"].lstrip("/")
    context.task_url = "http://dhos-janitor-api:5000/" + task_url


def populate_gdm_data(context: Context, days: int = 1) -> None:
    use_fixture(get_system_token, context)

    response = requests.post(
        "http://dhos-janitor-api:5000/dhos/v1/populate_gdm_task",
        headers={"Authorization": f"Bearer {context.system_jwt}"},
        params={"days": days, "use_system_jwt": True},
        timeout=30,
    )
    assert response.status_code == 202, f"{response.status_code} {response.text}"
    task_url = response.headers["Location"].lstrip("/")
    context.task_url = "http://dhos-janitor-api:5000/" + task_url


def is_task_completed(context: Context, name: str = "running task") -> bool:
    use_fixture(get_system_token, context)

    response = requests.get(
        context.task_url,
        headers={"Authorization": f"Bearer {context.system_jwt}"},
        timeout=30,
    )

    assert response.status_code in (
        200,
        202,
    ), f"{response.status_code} {response.text}"
    if response.status_code == 200:
        del context.task_url
        return True
    return False


def post_patient(context: Context, patient: Dict) -> str:
    generate_system_token(context)

    response = requests.post(
        "http://gdm-bff:5000/gdm/v1/internal/patient",
        params={"type": "GDM"},
        headers={"Authorization": f"Bearer {context.system_jwt}"},
        json=patient,
        timeout=60,
    )
    assert response.status_code == 200, f"{response.status_code} {response.text}"
    return response.json()["uuid"]


def get_patient(context: Context, patient_uuid: str) -> Dict:
    generate_superclinician_token(context)

    response = requests.get(
        f"http://gdm-bff:5000/gdm/v2/patient/{patient_uuid}",
        params={"type": "GDM"},
        headers={"Authorization": f"Bearer {context.superclinician_jwt}"},
        timeout=30,
    )
    assert response.status_code == 200, f"{response.status_code} {response.text}"
    return response.json()


def search_patients(context: Context, product: str) -> List[Dict]:
    generate_system_token(context)

    response = requests.get(
        "http://gdm-bff:5000/gdm/v1/internal/patient/search",
        params={"product_name": product, "active": True},  # type: ignore
        headers={"Authorization": f"Bearer {context.system_jwt}"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def patient_search_fuego(context: Context, mrn: str) -> List[Dict]:
    generate_system_token(context)

    response = requests.post(
        f"http://dhos-fuego-api:5000/dhos/v1/patient_search",
        headers={"Authorization": f"Bearer {context.system_jwt}"},
        json={"mrn": mrn},
    )
    response.raise_for_status()

    return response.json()


def get_all_patients_fuego(context: Context) -> List[Dict]:
    generate_system_token(context)

    response = requests.get(
        f"http://dhos-fuego-api:5000/dhos/v1/patient_search",
        headers={"Authorization": f"Bearer {context.system_jwt}"},
    )
    response.raise_for_status()

    return response.json()


def post_clinician(context: Context, clinician: Dict) -> dict:
    use_fixture(get_system_token, context)

    response = requests.post(
        "http://gdm-bff:5000/gdm/v1/clinician",
        params={"send_welcome_email": False},
        headers={"Authorization": f"Bearer {context.system_jwt}"},
        json=clinician,
        timeout=60,
    )
    assert response.status_code == 200
    return response.json()
