import random
from typing import Any, Dict, List, Protocol

from she_data_generation.person import (
    PhoneNumber,
    Sex,
    email_address,
    first_name,
    last_name,
    phone_number,
)

from .string import random_string
from .time import date

CLINICIAN_JOB_TITLES = [
    "Doctor",
    "Nurse",
    "Student",
    "Clinical support worker",
    "Allied healthcare professional",
]


class ClinicianCreator(Protocol):
    def __call__(self) -> Dict[str, Any]:
        ...


def clinician_product(product_name: str) -> Dict[str, str]:
    return {"product_name": product_name, "opened_date": date()}


def clinician_job_title() -> str:
    return random.choice(CLINICIAN_JOB_TITLES)


def smart_card_number() -> str:
    number = random_string(length=10, letters=False, digits=True)
    return f"@{number}"


def send_entry_identifier() -> str:
    number = random_string(length=10, letters=False, digits=True)
    return number


def clinician_factory(
    groups: List[str],
    product_name: str,
    locations: List[str] = None,
    clinician_sex: Sex = None,
) -> ClinicianCreator:
    sex: Sex = clinician_sex or Sex.random_choice()

    def generate() -> Dict[str, Any]:

        forename = first_name(sex)
        surname = last_name(sex)

        return {
            "first_name": forename,
            "last_name": surname,
            "phone_number": phone_number(phone_number_type=PhoneNumber.MOBILE),
            "job_title": clinician_job_title(),
            "nhs_smartcard_number": smart_card_number(),
            "send_entry_identifier": send_entry_identifier(),
            "locations": locations or [],
            "groups": groups,
            "products": [clinician_product(product_name)],
            "email_address": email_address(first_name=forename, last_name=surname),
        }

    return generate
