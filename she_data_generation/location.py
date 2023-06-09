import enum
import random
from typing import Any, Dict, Optional, Protocol

import draymed.codes

from ._faker import faker
from .string import segmented_string_factory
from .time import date


class Location(enum.Enum):
    WARD = draymed.codes.code_from_name("ward", category="location")
    HOSPITAL = draymed.codes.code_from_name("hospital", category="location")
    BAY = draymed.codes.code_from_name("bay", category="location")
    BED = draymed.codes.code_from_name("bed", category="location")
    CLINIC = draymed.codes.code_from_name("clinic", category="location")

    @classmethod
    def random_choice(cls) -> "Location":
        return random.choice([cls.WARD, cls.HOSPITAL, cls.BAY, cls.BED])


class LocationCreator(Protocol):
    def __call__(self) -> Dict[str, Any]:
        ...


def location_product(product_name: str) -> Dict[str, Any]:
    return {"product_name": product_name, "opened_date": date()}


def location_name() -> str:
    return faker.city() + " Ward"


def location_factory(
    *,
    product_name: str,
    loc_type: Optional[Location] = None,
    parent_ods_code: Optional[str] = None,
    parent_id: Optional[str] = None,
) -> LocationCreator:
    string_gen = segmented_string_factory(letters=True, digits=True, splitter="-")

    def generate() -> Dict[str, Any]:
        location = {
            "dh_products": [location_product(product_name)],
            "location_type": (loc_type or Location.random_choice()).value,
            "ods_code": string_gen(3, 3, 3),
            "display_name": location_name(),
            "parent_ods_code": parent_ods_code,
            "parent": parent_id,
        }
        return location

    return generate
