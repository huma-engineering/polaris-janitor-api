import random
import string
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from draymed import codes
from flask_batteries_included.helpers.timestamp import (
    parse_date_to_iso8601,
    parse_datetime_to_iso8601,
)
from she_data_generation.patient import nhs_number as sdg_nhs_number  # type: ignore

from dhos_janitor_api.helpers import names

HOUSE_NAMES = [
    "The Amazons",
    "School House",
    "Ivy Cottage",
    "The White House",
    "Number Ten",
    "The Barn",
]

ROAD_NAMES = [
    "High Street",
    "Second Avenue",
    "Little Timber Road",
    "Iron Peach Pike",
    "Cinder Blossom Street",
    "Orange Pond Farms",
    "Mill Byway",
    "Stony Bridge Park",
    "Still Nest Street",
    "Bleak Trout Street",
]

AREAS = [
    ("Oxford", "Oxfordshire", "OX"),
    ("Cambridge", "Cambridgeshire", "CB"),
    ("Canterbury", "Kent", "CT"),
    ("Nottingham", "Nottinghamshire", "NG"),
    ("Reading", "Berkshire", "RG"),
    ("Manchester", "Greater Manchester", "M"),
    ("Putney", "Wandsworth", "SW"),
    ("Chelsea", "Kensington and Chelsea", "SW"),
]

DATES_OF_BIRTH = [
    "1999-10-01",
    "1985-07-01",
    "1992-04-23",
    "1990-07-17",
    "1998-01-02",
    "2000-04-23",
    "1987-12-12",
    "1981-12-23",
]

NOTES = [
    "The patient looked well today",
    "Patient is doing brilliantly",
    "Patient expressed concerns about blood glucose levels",
    "Reminded patients to add comments to blood glucose readings",
    "Asked patients to tag their readings",
    "Need to ask patient about their meal schedule",
    "Note to check on patient's medication",
    "Patient has been struggling lately",
    "Discussed diet with patient",
    "Had good discussion with patient about managing blood glucose levels",
]

DIAGNOSIS_TOOL_OPTIONS = [
    [codes.code_from_name("nice20080hr", "diagnosis_tool")],
    [codes.code_from_name("nice20092hr", "diagnosis_tool")],
    [codes.code_from_name("nice20150hr", "diagnosis_tool")],
    [
        codes.code_from_name("nice20092hr", "diagnosis_tool"),
        codes.code_from_name("nice20150hr", "diagnosis_tool"),
    ],
]

DIABETES_TYPES_PREGNANT = (
    3 * [codes.code_from_name("gdm", "diabetes_type")]
    + 2 * [codes.code_from_name("preGdm", "diabetes_type")]
    + [
        codes.code_from_name("type1", "diabetes_type"),
        codes.code_from_name("type2", "diabetes_type"),
        codes.code_from_name("mody", "diabetes_type"),
        codes.code_from_name("other", "diabetes_type"),
    ]
)

DIABETES_TYPES_NOT_PREGNANT = 4 * [codes.code_from_name("type2", "diabetes_type")] + [
    codes.code_from_name("type1", "diabetes_type"),
    codes.code_from_name("other", "diabetes_type"),
]


def data_lists() -> Dict:
    postnatal_stay = random.randrange(1, 6)
    expected_babies = random.randrange(1, 3)
    observable_entity = list(codes.list_category("observable_entity").keys())
    routine_sct_code = list(codes.list_category("routine_sct_code").keys())
    mrn_number = "".join(
        random.choice(string.digits) for _ in range(random.randrange(6, 12))
    )

    data_dict = {
        "random_dob": random.choice(DATES_OF_BIRTH),
        "postnatal_stay": postnatal_stay,
        "expected_babies": expected_babies,
        "observable_entity": observable_entity,
        "routine_sct_code": routine_sct_code,
        "mrn_number": mrn_number,
    }

    return data_dict


def generate_nhs_number() -> str:
    return sdg_nhs_number()


def convert_time(dt: datetime) -> datetime:
    td = timedelta(seconds=0)
    tz = timezone(td)
    dt = dt.replace(tzinfo=tz)

    return dt


def generate_conception_date() -> datetime:
    start = datetime.utcnow() - timedelta(weeks=20)
    end = start - timedelta(weeks=20)
    conception = start + (end - start) * random.random()

    return convert_time(conception)


def generate_send_start_date() -> datetime:
    start = datetime.utcnow() - timedelta(weeks=1)
    end = start - timedelta(weeks=10)
    return convert_time(start + (end - start) * random.random())


def pregnancy_dates(conception: datetime) -> Dict:
    presented_date_working = conception + timedelta(days=20)
    diagnosed_date_working = presented_date_working + timedelta(days=20)
    estimated_delivery_date_working = conception + timedelta(days=280)

    presented_date = presented_date_working
    diagnosed_date = diagnosed_date_working
    diagnosed_date_only = parse_date_to_iso8601(diagnosed_date)
    diagnosed_date_iso8601 = parse_datetime_to_iso8601(diagnosed_date)
    estimated_delivery_date = estimated_delivery_date_working
    estimated_delivery_date_only = parse_date_to_iso8601(estimated_delivery_date)

    date_dict = {
        "conception_timing": conception,
        "presented_date": presented_date,
        "diagnosed_date": diagnosed_date,
        "estimated_delivery_date": estimated_delivery_date,
        "diagnosed_date_only": diagnosed_date_only,
        "diagnosed_date_iso8601": diagnosed_date_iso8601,
        "estimated_delivery_date_only": estimated_delivery_date_only,
    }

    return date_dict


def generate_random_delivery(clinician_uuid: str, conception_date: datetime) -> Dict:
    pregnancy_reference_dates = pregnancy_dates(conception_date)

    birth_outcome = random.choice(list(codes.list_category("birth_outcome").keys()))
    outcome_for_baby = random.choice(
        list(codes.list_category("outcome_for_baby").keys())
    )
    neonatal_complications = random.choice(
        list(codes.list_category("neonatal_complications").keys())
    )
    neonatal_complications_other = (
        "Minor problems"
        if neonatal_complications
        == codes.code_from_name("neonatalOther", "neonatal_complications")
        else ""
    )
    admitted_to_special_baby_care_unit = random.choice([True, False])
    birth_weight_in_grams = int(random.randint(1000, 4000))
    length_of_postnatal_stay_for_baby = random.randint(0, 4)
    apgar_1_minute = random.randint(1, 10)
    apgar_5_minute = min(10, apgar_1_minute + 2)
    feeding_method = random.choice(list(codes.list_category("feeding_method").keys()))
    baby_first_name = names.first_name()
    baby_surname = names.last_name()

    random_delivery = {
        "birth_outcome": birth_outcome,
        "outcome_for_baby": outcome_for_baby,
        "neonatal_complications": neonatal_complications,
        "neonatal_complications_other": neonatal_complications_other,
        "admitted_to_special_baby_care_unit": admitted_to_special_baby_care_unit,
        "birth_weight_in_grams": birth_weight_in_grams,
        "length_of_postnatal_stay_for_baby": length_of_postnatal_stay_for_baby,
        "apgar_1_minute": apgar_1_minute,
        "apgar_5_minute": apgar_5_minute,
        "feeding_method": feeding_method,
        "patient": {
            "first_name": baby_first_name,
            "last_name": baby_surname,
            "dob": pregnancy_reference_dates["estimated_delivery_date"],
        },
        "created": pregnancy_reference_dates["estimated_delivery_date"],
        "created_by": clinician_uuid,
        "modified": pregnancy_reference_dates["estimated_delivery_date"],
        "modified_by": clinician_uuid,
    }

    return random_delivery


def generate_pregnancy(conception_date: datetime, clinician_uuid: str) -> Dict:
    pregnancy_reference_dates = pregnancy_dates(conception_date)

    pregnancy_complication = random.choice(
        list(codes.list_category("pregnancy_complications").keys())
    )

    height_at_booking_in_mm = int(random.randint(1400, 2000))
    weight_at_diagnosis_in_g = int(random.randint(50000, 100_000))
    weight_at_booking_in_g = int(weight_at_diagnosis_in_g * 1.1)
    weight_at_36_weeks_in_g = int(weight_at_booking_in_g * 1.1)

    expected_number_of_babies = random.choice([1, 2])

    random_pregnancy = {
        "estimated_delivery_date": pregnancy_reference_dates[
            "estimated_delivery_date_only"
        ],
        "planned_delivery_place": "99b1668c-26f1-4aec-88ca-597d3a20d977",
        "length_of_postnatal_stay_in_days": data_lists()[
            "postnatal_stay"
        ],  # random (1-5)
        "colostrum_harvesting": True,
        "expected_number_of_babies": expected_number_of_babies,
        "deliveries": [],
        "height_at_booking_in_mm": height_at_booking_in_mm,
        "weight_at_diagnosis_in_g": weight_at_diagnosis_in_g,
        "weight_at_booking_in_g": weight_at_booking_in_g,
        "weight_at_36_weeks_in_g": weight_at_36_weeks_in_g,
        "pregnancy_complications": [pregnancy_complication],
        "created": pregnancy_reference_dates["diagnosed_date_iso8601"],
        "created_by": clinician_uuid,
        "modified": pregnancy_reference_dates["diagnosed_date_iso8601"],
        "modified_by": clinician_uuid,
    }

    random_pregnancy_with_delivery = {
        "estimated_delivery_date": pregnancy_reference_dates[
            "estimated_delivery_date_only"
        ],
        "planned_delivery_place": "99b1668c-26f1-4aec-88ca-597d3a20d977",
        "length_of_postnatal_stay_in_days": random.randint(1, 5),
        "colostrum_harvesting": True,
        "expected_number_of_babies": expected_number_of_babies,
        "deliveries": [
            generate_random_delivery(clinician_uuid, conception_date)
            for _ in range(expected_number_of_babies)
        ],
        "height_at_booking_in_mm": height_at_booking_in_mm,
        "weight_at_diagnosis_in_g": weight_at_diagnosis_in_g,
        "weight_at_booking_in_g": weight_at_booking_in_g,
        "weight_at_36_weeks_in_g": weight_at_36_weeks_in_g,
        "pregnancy_complications": [pregnancy_complication],
        "created": pregnancy_reference_dates["diagnosed_date_iso8601"],
        "created_by": clinician_uuid,
        "modified": pregnancy_reference_dates["diagnosed_date_iso8601"],
        "modified_by": clinician_uuid,
    }

    pregnancy_dict = {
        "random_pregnancy": random_pregnancy,
        "random_pregnancy_with_delivery": random_pregnancy_with_delivery,
    }

    return pregnancy_dict


def generate_diabetes_diagnosis(
    conception_date: datetime,
    clinician_uuid: str,
    medications: List[Dict],
    is_pregnant: bool,
    diagnosis_tool_other: Optional[str] = None,
) -> Dict:
    random_medication = random.choice(medications)
    pregnancy_reference_dates = pregnancy_dates(conception_date)

    if diagnosis_tool_other is None:
        diagnosis_tool_other = random.choice([None, None, "Predictive algorithm"])

    diagnosis_tool = random.choice(DIAGNOSIS_TOOL_OPTIONS)

    if (
        diagnosis_tool_other and "D0000018" not in diagnosis_tool
    ):  # https://sensynehealth.atlassian.net/browse/PLAT-698
        diagnosis_tool.append("D0000018")

    if is_pregnant:
        sct_code = random.choice(DIABETES_TYPES_PREGNANT)
        obs_entities = [
            {
                "sct_code": codes.code_from_name("HbA1cTest", "observable_entity"),
                "date_observed": pregnancy_reference_dates["diagnosed_date_only"],
                "value_as_string": "2",
                "metadata": {"tag": "first"},
            },
            {
                "sct_code": codes.code_from_name("HbA1cTest", "observable_entity"),
                "date_observed": pregnancy_reference_dates[
                    "estimated_delivery_date_only"
                ],
                "value_as_string": "5",
                "metadata": {"tag": "last"},
            },
        ]
        obs_entities_choice = [
            None,
            [obs_entities[0]],
            [obs_entities[0], obs_entities[1]],
            [obs_entities[1]],
        ]
    else:
        sct_code = random.choice(DIABETES_TYPES_NOT_PREGNANT)
        [
            {
                "sct_code": codes.code_from_name(
                    "bloodGlucoseTest", "observable_entity"
                ),
                "date_observed": pregnancy_reference_dates["diagnosed_date_only"],
                "value_as_string": "A value",
            }
        ],
        obs_entities_choice = [
            None,
            [
                {
                    "sct_code": codes.code_from_name(
                        "bloodGlucoseTest", "observable_entity"
                    ),
                    "date_observed": pregnancy_reference_dates["diagnosed_date_only"],
                    "value_as_string": "A value",
                }
            ],
        ]

    diagnosis_other = (
        "post pancreatectomy"
        if sct_code == codes.code_from_name("other", "diabetes_type")
        else None
    )

    random_diagnosis = {
        "sct_code": sct_code,
        "diagnosis_other": diagnosis_other,
        "diagnosed": pregnancy_reference_dates["diagnosed_date_only"],
        "episode": 1,
        "presented": parse_date_to_iso8601(pregnancy_reference_dates["diagnosed_date"]),
        "diagnosis_tool": diagnosis_tool,
        "diagnosis_tool_other": diagnosis_tool_other,
        "risk_factors": [codes.code_from_name("bmi", "risk_factor")],
        "observable_entities": random.choice(obs_entities_choice),
        "management_plan": {
            "start_date": pregnancy_reference_dates["diagnosed_date_only"],
            "end_date": pregnancy_reference_dates["estimated_delivery_date_only"],
            "sct_code": codes.code_from_name("insulin", "management_type"),
            "doses": [
                {
                    "medication_id": random_medication["sct_code"],
                    "dose_amount": random.choice([0.5, 1.0, 1.5, 2.0]),
                    "routine_sct_code": random.choice(data_lists()["routine_sct_code"]),
                }
            ],
            "actions": [{"action_sct_code": "12345"}],
        },
        "readings_plan": {
            "start_date": pregnancy_reference_dates["diagnosed_date_only"],
            "end_date": pregnancy_reference_dates["estimated_delivery_date_only"],
            "sct_code": "54321",
            "days_per_week_to_take_readings": 7,
            "readings_per_day": random.choice([2, 4, 7]),
        },
        "created": pregnancy_reference_dates["diagnosed_date_iso8601"],
        "created_by": clinician_uuid,
        "modified": pregnancy_reference_dates["diagnosed_date_iso8601"],
        "modified_by": clinician_uuid,
    }

    return random_diagnosis


def generate_visit(
    visit_date: datetime,
    clinician_uuid: str = "static_clinician_uuid_D",
    location_uuid: str = "static_location_uuid_L2",
) -> Dict:
    return {
        "visit_date": parse_datetime_to_iso8601(visit_date),
        "summary": "Talked about diabetes",
        "location": location_uuid,
        "clinician_uuid": clinician_uuid,
        "diagnoses": [],
        "created": parse_datetime_to_iso8601(visit_date),
        "created_by": clinician_uuid,
        "modified": parse_datetime_to_iso8601(visit_date),
        "modified_by": clinician_uuid,
    }


def generate_notes(
    conception_date: datetime, clinician_uuid: str = "static_clinician_uuid_D"
) -> List[Dict]:
    # Random number of notes between 0 and equivalent of one per week.
    date_difference = datetime.utcnow().date() - conception_date.date()
    max_num_notes: int = random.randint(0, max(0, date_difference.days // 7))

    notes: List[Dict] = []
    for i in range(max_num_notes):
        note_date: datetime = (
            datetime.utcnow()
            - timedelta(random.randint(0, date_difference.days))
            - timedelta(minutes=random.randint(0, 60 * 12))
        )
        note_date = note_date.replace(tzinfo=timezone.utc)

        notes.append(
            {
                "content": random.choice(NOTES),
                "clinician_uuid": clinician_uuid,
                "created": parse_datetime_to_iso8601(note_date),
                "modified": parse_datetime_to_iso8601(note_date),
            }
        )
    return notes


def generate_diabetes_record(
    clinician_uuid: str,
    conception_date: datetime,
    medications: List[Dict],
    is_pregnant: bool = True,
    closed: bool = False,
) -> Dict:
    pregnancy_reference_dates = pregnancy_dates(conception_date)

    pregnancies: List[Dict] = []
    history: Dict = {}
    if is_pregnant:
        pregnancy_key = (
            "random_pregnancy_with_delivery" if closed else "random_pregnancy"
        )
        pregnancies = [
            generate_pregnancy(conception_date, clinician_uuid)[pregnancy_key]
        ]
        gravidity = random.randint(1, 20)
        history = {
            "gravidity": gravidity,
            "parity": min(gravidity, random.randint(0, 3)),
        }

    record = {
        "notes": generate_notes(conception_date, clinician_uuid),
        "history": history,
        "pregnancies": pregnancies,
        "diagnoses": [
            generate_diabetes_diagnosis(
                conception_date, clinician_uuid, medications, is_pregnant
            )
        ],
        "visits": [generate_visit(conception_date)],
        "created": pregnancy_reference_dates["diagnosed_date_iso8601"],
        "created_by": clinician_uuid,
        "modified": pregnancy_reference_dates["diagnosed_date_iso8601"],
        "modified_by": clinician_uuid,
    }

    return record


def generate_send_record(clinician_uuid: str, start_date: datetime) -> Dict:
    record: Dict = {
        "notes": [],
        "diagnoses": [],
        "created": parse_datetime_to_iso8601(start_date),
        "created_by": clinician_uuid,
        "modified": parse_datetime_to_iso8601(start_date),
        "modified_by": clinician_uuid,
    }
    return record


def generate_personal_address(product_open_date: datetime) -> Dict:
    return {
        **generate_random_address(),
        **generate_current_personal_address_date(product_open_date),
    }


def generate_current_personal_address_date(product_open_date: datetime) -> Dict:
    # Add a few years to the product open date
    # In future this could return a list of dates

    lived_from_date = (
        product_open_date + timedelta(weeks=-1 * random.randint(200, 300))
    ).date()

    return {"lived_from": parse_date_to_iso8601(lived_from_date)}


def generate_random_address() -> Dict:
    road_name = random.choice(ROAD_NAMES)

    if random.randint(1, 10) < 4:
        house_name = random.choice(HOUSE_NAMES)
        address_line_1 = f"{house_name} {road_name}"
    else:
        house_number = str(random.randint(1, 200))
        address_line_1 = f"{house_number} {road_name}"

    locality, region, postcode_prefix = random.choice(AREAS)

    return {
        "address_line_1": address_line_1,
        "address_line_2": "",
        "address_line_3": "",
        "address_line_4": "",
        "locality": locality,
        "region": region,
        "postcode": generate_postcode_from_prefix(postcode_prefix),
    }


def generate_postcode_from_prefix(prefix: str) -> str:
    third = random.randint(1, 9)
    fourth = random.randint(1, 9)
    fifth = random.choice(string.ascii_uppercase)
    sixth = random.choice(string.ascii_uppercase)

    return f"{prefix}{third} {fourth}{fifth}{sixth}"
