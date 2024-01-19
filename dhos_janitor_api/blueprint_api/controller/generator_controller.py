import random
import uuid as _uuid
from datetime import datetime, timedelta
from typing import Dict, Optional

import draymed
from flask_batteries_included.helpers.timestamp import (
    parse_date_to_iso8601_typesafe,
    parse_datetime_to_iso8601_typesafe,
)

from dhos_janitor_api.blueprint_api.client import (
    ClientRepository,
    medication_client,
    trustomer_client,
    users_client,
)
from dhos_janitor_api.blueprint_api.controller import auth_controller
from dhos_janitor_api.data import patient_data
from dhos_janitor_api.helpers import names

EDUCATION_LEVELS = [e for e in draymed.codes.list_category("education_level")]


def generate_patient(
    clients: ClientRepository,
    product_name: str,
    closed: bool = False,
    uuid: Optional[str] = None,
    hospital_number: Optional[str] = None,
) -> Dict:
    system_jwt = auth_controller.get_system_jwt()
    new_patient_uuid = uuid or str(_uuid.uuid4())
    clinicians = users_client.get_clinicians(
        clients=clients,
        product_name=product_name,
        system_jwt=system_jwt,
    )
    random.shuffle(clinicians)
    random_clinician = next(
        (c for c in clinicians if c.get("locations") and c.get("uuid")), None
    )
    random_clinician_uuid = (
        random_clinician["uuid"] if random_clinician else "static_clinician_uuid_A"
    )
    random_location_uuid = (
        random.choice(random_clinician["locations"])
        if random_clinician
        else "static_location_uuid_L1"
    )
    last_name = names.last_name()
    nhs_number = patient_data.generate_nhs_number()
    mrn_number = (
        hospital_number
        if hospital_number is not None
        else patient_data.data_lists()["mrn_number"]
    )
    ethnicity = random.choice(list(draymed.codes.list_category("ethnicity").keys()))

    # Product-specific settings
    if product_name == "GDM":
        conception_date = patient_data.generate_conception_date()
        start_date = conception_date + timedelta(weeks=random.randint(6, 20))
        patient_sex = "female"

        gdm_medication_tags = trustomer_client.get_trustomer_config(
            clients=clients, system_jwt=system_jwt
        )["gdm_config"]["medication_tags"]
        gdm_medications = medication_client.get_medications(
            clients=clients,
            system_jwt=system_jwt,
            medication_tag=gdm_medication_tags[0],
        )

        record = patient_data.generate_diabetes_record(
            random_clinician_uuid,
            conception_date=conception_date,
            medications=gdm_medications,
            is_pregnant=True,
        )

        personal_addresses = [patient_data.generate_personal_address(start_date)]
        if random.random() < 0.5 and hospital_number is None:
            nhs_number = ""
        dh_products = [
            _gdm_product_fields(conception_date, random_clinician_uuid, closed)
        ]
        # 10% chance of a GDm patient also being a DBm patient
        if random.random() < 0.1:
            dbm_closed = random.choice([True, False])
            dh_products.append(
                _dbm_product_fields(conception_date, random_clinician_uuid, dbm_closed)
            )

    elif product_name == "DBM":
        conception_date = patient_data.generate_conception_date()
        start_date = conception_date + timedelta(weeks=random.randint(6, 20))
        patient_sex = random.choice(["female", "male"])

        dbm_medication_tags = trustomer_client.get_trustomer_config(
            clients=clients, system_jwt=system_jwt
        )["gdm_config"]["medication_tags"]
        dbm_medications = medication_client.get_medications(
            clients=clients,
            system_jwt=system_jwt,
            medication_tag=dbm_medication_tags[0],
        )

        record = patient_data.generate_diabetes_record(
            random_clinician_uuid,
            conception_date=conception_date,
            medications=dbm_medications,
            is_pregnant=False,
        )

        personal_addresses = [patient_data.generate_personal_address(start_date)]
        if random.random() < 0.5:
            nhs_number = ""
        dh_products = [
            _dbm_product_fields(conception_date, random_clinician_uuid, closed)
        ]

        random_location_uuid = (
            "static_organisation_uuid_O1"
            if new_patient_uuid.startswith("static_")
            else "static_organisation_uuid_O2"
        )

    elif product_name == "SEND":
        start_date = patient_data.generate_send_start_date()
        patient_sex = random.choice(["female", "male"])
        personal_addresses = []
        record = patient_data.generate_send_record(random_clinician_uuid, start_date)
        dh_products = [_send_product_fields(start_date, random_clinician_uuid)]

    else:
        raise NotImplementedError(
            f"Patient generation for product type {product_name} not yet implemented"
        )

    if patient_sex == "female":
        first_name = names.first_name_female()
    else:
        first_name = names.first_name_male()

    payload = {
        "allowed_to_text": False,
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": "07123456789",
        "dob": random.choice(patient_data.DATES_OF_BIRTH),
        "nhs_number": nhs_number,
        "hospital_number": mrn_number,
        "email_address": f"{first_name}@email.com",
        "dh_products": dh_products,
        "personal_addresses": personal_addresses,
        "ethnicity": ethnicity,
        "sex": draymed.codes.code_from_name(patient_sex, category="sex"),
        "highest_education_level": random.choice(EDUCATION_LEVELS),
        "accessibility_considerations": [],
        "other_notes": "",
        "record": record,
        "created": parse_datetime_to_iso8601_typesafe(start_date),
        "created_by": random_clinician_uuid,
        "modified": parse_datetime_to_iso8601_typesafe(start_date),
        "modified_by": random_clinician_uuid,
        "locations": [random_location_uuid],
        "uuid": new_patient_uuid,
    }

    return payload


def generate_fhir_patient() -> Dict:
    random_data = patient_data.data_lists()
    return {
        "mrn": random_data["mrn_number"],
        "first_name": names.first_name(),
        "last_name": names.last_name(),
        "date_of_birth": random_data["random_dob"],
    }


def generate_fhir_patient_from_dhos_services_patient(
    dhos_services_patient: Dict,
) -> Dict:
    return {
        "mrn": dhos_services_patient["hospital_number"],
        "first_name": dhos_services_patient["first_name"],
        "last_name": dhos_services_patient["last_name"],
        "date_of_birth": dhos_services_patient["dob"],
    }


def _common_product_fields(start_date: datetime, clinician_uuid: str) -> Dict:
    return {
        "accessibility_discussed": True,
        "accessibility_discussed_with": clinician_uuid,
        "accessibility_discussed_date": parse_date_to_iso8601_typesafe(start_date),
        "opened_date": parse_date_to_iso8601_typesafe(start_date),
        "created": parse_datetime_to_iso8601_typesafe(start_date),
        "created_by": clinician_uuid,
        "modified": parse_datetime_to_iso8601_typesafe(start_date),
        "modified_by": clinician_uuid,
    }


def _gdm_product_fields(
    conception_date: datetime, clinician_uuid: str, closed: bool
) -> Dict:
    start_date = patient_data.pregnancy_dates(conception_date)["diagnosed_date"]
    start_datetime = patient_data.pregnancy_dates(conception_date)["diagnosed_date"]
    fields = _common_product_fields(start_date, clinician_uuid)
    fields.update(
        {
            "modified": parse_datetime_to_iso8601_typesafe(
                patient_data.pregnancy_dates(conception_date)["diagnosed_date"]
            ),
            "product_name": "GDM",
            "created": parse_datetime_to_iso8601_typesafe(start_datetime),
        }
    )
    if closed:
        fields.update(
            {
                "modified": parse_datetime_to_iso8601_typesafe(
                    patient_data.pregnancy_dates(conception_date)[
                        "estimated_delivery_date"
                    ]
                ),
                "closed_date": parse_date_to_iso8601_typesafe(
                    patient_data.pregnancy_dates(conception_date)[
                        "estimated_delivery_date"
                    ]
                ),
                "closed_reason": "Closed for a very good reason",
            }
        )
    return fields


def _send_product_fields(start_date: datetime, clinician_uuid: str) -> Dict:
    return {
        **_common_product_fields(start_date, clinician_uuid),
        "product_name": "SEND",
    }


def _dbm_product_fields(
    conception_date: datetime, clinician_uuid: str, closed: bool
) -> Dict:
    start_date = patient_data.pregnancy_dates(conception_date)["diagnosed_date"]
    fields = _common_product_fields(start_date, clinician_uuid)
    fields["product_name"] = "DBM"
    if closed:
        fields.update(
            {
                "modified": parse_datetime_to_iso8601_typesafe(
                    patient_data.pregnancy_dates(conception_date)[
                        "estimated_delivery_date"
                    ]
                ),
                "closed_date": parse_date_to_iso8601_typesafe(
                    patient_data.pregnancy_dates(conception_date)[
                        "estimated_delivery_date"
                    ]
                ),
                "closed_reason": "Closed for a very good reason",
            }
        )
    return fields
