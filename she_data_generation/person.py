import random
from enum import Enum
from typing import Any, Optional

import draymed.codes

from ._faker import faker
from .string import random_string


class Sex(Enum):
    ANY = draymed.codes.code_from_name("indeterminate", category="sex")
    MALE = draymed.codes.code_from_name("male", category="sex")
    FEMALE = draymed.codes.code_from_name("female", category="sex")

    @classmethod
    def random_choice(cls) -> "Sex":
        return random.choice([cls.MALE, cls.FEMALE])


_sex_suffix = {Sex.ANY: "", Sex.MALE: "_male", Sex.FEMALE: "_female"}


class PhoneNumber(Enum):
    # phone number stuff
    MOBILE = 0
    LANDLINE = 1

    @classmethod
    def random_choice(cls) -> "PhoneNumber":
        return random.choice([cls.MOBILE, cls.LANDLINE])


def _gen(name: str, sex: Sex = Sex.ANY) -> str:
    method_suffix = _sex_suffix[sex]
    method = getattr(faker, f"{name}{method_suffix}")
    return method()


def title(sex: Sex = Sex.ANY) -> str:
    return _gen("prefix", sex=sex)


def first_name(sex: Sex = Sex.ANY) -> str:
    return _gen("first_name", sex=sex)


def last_name(sex: Sex = Sex.ANY) -> str:
    return _gen("last_name", sex=sex)


def suffix(sex: Sex = Sex.ANY) -> str:
    return _gen("suffix", sex=sex)


def full_name(
    sex: Sex = Sex.ANY, include_title: bool = False, include_suffix: bool = False
) -> str:
    forename = first_name(sex=sex)
    surname = last_name(sex=sex)
    name = f"{forename} {surname}"
    if include_title:
        name_prefix = title(sex=sex)
        name = f"{name_prefix} {name}"
    if include_suffix:
        name_suffix = suffix(sex=sex)
        name = f"{name} {name_suffix}"
    return name


def email_address(
    first_name: str = None,
    last_name: str = None,
    slug: Optional[Any] = None,
    domain: Optional[Any] = None,
) -> str:
    if not slug:
        slug = random_string(2, digits=True, letters=False)
    if not domain:
        domain = faker.domain_name()
    if first_name and last_name:
        return f"{first_name}.{last_name}@{domain}"
    elif first_name:
        return f"{first_name}{slug}@{domain}"
    elif last_name:
        return f"{last_name}{slug}@{domain}"
    return faker.email(domain=domain)


def mobile_phone_number() -> str:
    prefix = "07700"  # makes it very unlikely to be a real phone number
    number = random_string(length=6, letters=False, digits=True)
    return f"{prefix}{number}"


def land_line_phone_number() -> str:
    prefix = "01632"  # makes it very unlikely to be a real phone number
    number = random_string(length=6, letters=False, digits=True)
    return f"{prefix}{number}"


def phone_number(phone_number_type: PhoneNumber = None) -> str:
    if not phone_number_type:
        phone_number_type = PhoneNumber.random_choice()
    if phone_number_type == PhoneNumber.MOBILE:
        return mobile_phone_number()
    if phone_number_type == PhoneNumber.LANDLINE:
        return land_line_phone_number()
    raise ValueError(f"invalid phone number type: {phone_number_type}")
