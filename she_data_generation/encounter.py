import random
from typing import Any, Dict, Protocol

from .time import datetime
from .uid import uuid4

ENCOUNTER_TYPES = ["test", "other"]


class EncounterCreator(Protocol):
    def __call__(self, score_system: str = "news2") -> Dict[str, Any]:
        ...


def encounter_type() -> str:
    return random.choice(ENCOUNTER_TYPES)


def encounter_factory() -> EncounterCreator:
    def generate(score_system: str = "news2") -> Dict[str, Any]:
        return {
            "encounter_type": encounter_type(),
            "admitted_at": datetime(),
            "epr_encounter_id": uuid4(),
            "score_system": score_system,
        }

    return generate
