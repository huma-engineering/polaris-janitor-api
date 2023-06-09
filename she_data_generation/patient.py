from typing import Any, Dict, List, Protocol

from .person import PhoneNumber, Sex, email_address, first_name, last_name, phone_number
from .string import random_string
from .time import date, date_of_birth


def nhs_number() -> str:
    """
    An NHS number must be 10 digits, where the last digit is a check digit using the modulo 11 algorithm
    (see https://datadictionary.nhs.uk/attributes/nhs_number.html).
    """
    first_nine: str = random_string(length=9, letters=False, digits=True)
    digits: List[int] = list(map(int, list(first_nine)))
    total = sum((10 - i) * digit for i, digit in enumerate(digits))
    check_digit = 11 - (total % 11)
    if check_digit == 10:
        # Invalid - try again
        return nhs_number()
    if check_digit == 11:
        check_digit = 0
    return first_nine + str(check_digit)


def hospital_number() -> str:
    return random_string(length=12, letters=False, digits=True)


def patient_product(product_name: str) -> Dict[str, str]:
    return {"product_name": product_name, "opened_date": date()}


class PatientCreator(Protocol):
    def __call__(self) -> Dict[str, Any]:
        ...


def patient_factory(
    locations: List[str], product_name: str, patient_sex: Sex = None
) -> PatientCreator:
    sex: Sex = patient_sex or Sex.random_choice()

    def generate() -> Dict[str, Any]:
        forename = first_name(sex)
        surname = last_name(sex)
        return {
            "first_name": forename,
            "last_name": surname,
            "phone_number": phone_number(phone_number_type=PhoneNumber.MOBILE),
            "dob": date_of_birth(min_age=16),
            "hospital_number": hospital_number(),
            "nhs_number": nhs_number(),
            "allowed_to_text": True,
            "email_address": email_address(first_name=forename, last_name=surname),
            "sex": sex.value,
            "record": {},
            "locations": locations,
            "dh_products": [patient_product(product_name=product_name)],
        }

    return generate
