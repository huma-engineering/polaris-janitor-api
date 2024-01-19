import random
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Union

from .time import datetime

SCORE_SYSTEMS = ["news2", "meows"]

OBSERVATION_TYPES = [
    "spo2",
    "nurse_concern",
    "consciousness_acvpu",
    "o2_therapy_status",
    "respiratory_rate",
    "heart_rate",
    "blood_pressure",
    "temperature",
]

OBSERVATIONS_UNABLE_TO_REFUSE = [
    "o2_therapy_status",
    "consciousness_acvpu",
    "nurse_concern",
]

NURSE_CONCERNS = [
    "Airway Compromise",
    "Bleeding/Melaena",
    "Pallor or Cyanosis",
    "New Facial/Limb Weakness",
    "Diarrhoea/Vomiting",
    "Abnormal Electrolyte/BG",
    "Unresolved Pain",
    "Self Harm",
    "Infection?",
    "Shock (HR > BP)",
    "Non-specific Concern",
]

REQUIRED_OBS = [
    "spo2",
    "consciousness_acvpu",
    "o2_therapy_status",
    "respiratory_rate",
    "heart_rate",
    "blood_pressure",
    "temperature",
    "systolic_blood_pressure",
    "diastolic_blood_pressure",
]

MASKS = [  # TODO get from trustomer
    "Venturi",
    "Humidified",
    "Nasal Cann.",
    "Simple",
    "Resv Mask",
    "CPAP",
    "NIV",
    "High Flow",
]


class Trajectory(Enum):
    VERY_ILL = 0
    MEDIUM_ILL = 1
    A_BIT_ILL = 2
    FINE = 3

    @staticmethod
    def random_choice() -> "Trajectory":
        rand = random.random()
        if rand < 0.75:
            return Trajectory.FINE
        if rand < 0.90:
            return Trajectory.A_BIT_ILL
        if rand < 0.95:
            return Trajectory.MEDIUM_ILL
        return Trajectory.VERY_ILL


class ObsSetGenerator:
    def __init__(
        self,
        trajectory: Trajectory,
        observation_probability: float,
        refuse_all: bool = False,
        score_system: Optional[str] = None,
    ):
        self.trajectory = trajectory
        self.observation_probability = observation_probability
        self.refuse_all = refuse_all
        self.score_system = score_system

    def consciousness_acvpu(self) -> Dict[str, str]:
        if self.trajectory == Trajectory.FINE:
            consciousness = "Alert"
        elif self.trajectory == Trajectory.A_BIT_ILL:
            consciousness = random.choice(["Alert", "Confusion"])
        elif self.trajectory == Trajectory.MEDIUM_ILL:
            consciousness = random.choice(["Alert", "Confusion", "Voice"])
        else:
            consciousness = random.choice(
                ["Confusion", "Voice", "Pain", "Unresponsive"]
            )

        return {"observation_string": consciousness}

    def spo2(self) -> Dict[str, Any]:
        if self.trajectory == Trajectory.FINE:
            greater_than = 96
            less_than = 100
        elif self.trajectory == Trajectory.A_BIT_ILL:
            greater_than = 94
            less_than = 100
        elif self.trajectory == Trajectory.MEDIUM_ILL:
            greater_than = 92
            less_than = 100
        else:
            greater_than = 80
            less_than = 100
        value = random.randint(greater_than, less_than)
        return {"observation_value": value, "observation_unit": "%"}

    def nurse_concern(self) -> Optional[Dict[str, str]]:
        if self.trajectory == Trajectory.FINE:
            threshold = 0.95
        elif self.trajectory == Trajectory.A_BIT_ILL:
            threshold = 0.9
        elif self.trajectory == Trajectory.MEDIUM_ILL:
            threshold = 0.6
        else:
            threshold = 0.4
        if random.random() < threshold:
            return None

        return {"observation_string": random.choice(NURSE_CONCERNS)}

    def o2_therapy_status(self) -> Dict[str, Any]:

        if self.trajectory == Trajectory.FINE:
            threshold = 0.95
        elif self.trajectory == Trajectory.A_BIT_ILL:
            threshold = 0.85
        elif self.trajectory == Trajectory.MEDIUM_ILL:
            threshold = 0.5
        else:
            threshold = 0.2

        if random.random() < threshold:
            return {
                "observation_value": 0,
                "observation_unit": "lpm",
                "observation_metadata": {"mask": "Room Air"},
            }

        mask: str = random.choice(MASKS)
        observation_metadata: Dict[str, Union[str, int]] = {"mask": mask}
        observation_value: Union[float, int]

        if mask == "High Flow":
            observation_value = random.randint(1, 100)
            observation_unit = "%"
        else:
            observation_value = round(random.uniform(0.5, 15), 1)
            observation_unit = "lpm"
        if mask == "Venturi":
            observation_metadata["mask_percent"] = random.choice([24, 28, 35, 40, 60])
        elif mask == "Humidified":
            observation_metadata["mask_percent"] = random.choice(
                [28, 35, 40, 60, 80, 98]
            )

        return {
            "observation_type": "o2_therapy_status",
            "observation_value": observation_value,
            "observation_unit": observation_unit,
            "observation_metadata": observation_metadata,
        }

    def respiratory_rate(self) -> Dict[str, Any]:
        if self.trajectory == Trajectory.FINE:
            greater_than = 12
            less_than = 20
        elif self.trajectory == Trajectory.A_BIT_ILL:
            greater_than = 9
            less_than = 24
        elif self.trajectory == Trajectory.MEDIUM_ILL:
            greater_than = 7
            less_than = 30
        else:
            greater_than = 5
            less_than = 60
        value = random.randint(greater_than, less_than)
        return {"observation_value": value, "observation_unit": "per min"}

    def heart_rate(self) -> Dict[str, Any]:
        if self.trajectory == Trajectory.FINE:
            greater_than = 51
            less_than = 90
        elif self.trajectory == Trajectory.A_BIT_ILL:
            greater_than = 50
            less_than = 110
        elif self.trajectory == Trajectory.MEDIUM_ILL:
            greater_than = 40
            less_than = 130
        else:
            greater_than = 35
            less_than = 180
        value = random.randint(greater_than, less_than)

        return {"observation_value": value, "observation_unit": "bpm"}

    def blood_pressure(self) -> List[Dict[str, Any]]:
        if self.trajectory == Trajectory.FINE:
            greater_than = 110
            less_than = 140
        elif self.trajectory == Trajectory.A_BIT_ILL:
            greater_than = 100
            less_than = 150
        elif self.trajectory == Trajectory.MEDIUM_ILL:
            greater_than = 90
            less_than = 200
        else:
            greater_than = 80
            less_than = 240
        systolic_value: int = random.randint(greater_than, less_than)
        diastolic_value: int = systolic_value - random.randint(40, 60)
        position: str = random.choice(["sitting", "standing", "lying"])

        observations = [
            {
                "patient_refused": False,
                "observation_type": "systolic_blood_pressure",
                "observation_value": systolic_value,
                "observation_unit": "mmHg",
                "observation_metadata": {"patient_position": position},
                "measured_time": datetime(),
            },
            {
                "patient_refused": False,
                "observation_type": "diastolic_blood_pressure",
                "observation_value": diastolic_value,
                "observation_unit": "mmHg",
                "observation_metadata": {"patient_position": position},
                "measured_time": datetime(),
            },
        ]
        if random.random() > 0.95:
            for obs in observations:
                obs["patient_refused"] = True
                obs.pop("observation_value", None)
                obs.pop("observation_string", None)
                obs.pop("observation_metadata", None)

        return observations

    def temperature(self) -> Dict[str, Any]:
        if self.trajectory == Trajectory.FINE:
            greater_than = 36.5
            less_than = 37.5
        elif self.trajectory == Trajectory.A_BIT_ILL:
            greater_than = 36
            less_than = 38.5
        elif self.trajectory == Trajectory.MEDIUM_ILL:
            greater_than = 35
            less_than = 39
        else:
            greater_than = 34
            less_than = 40
        value = round(random.uniform(greater_than, less_than), 1)
        return {"observation_value": value, "observation_unit": "celcius"}

    def generate_observation(self, observation_type: str) -> List[Dict[str, Any]]:
        observation: Dict[str, Any] = {
            "observation_type": observation_type,
            "measured_time": datetime(),
        }
        can_refuse = observation_type not in OBSERVATIONS_UNABLE_TO_REFUSE

        if observation_type == "blood_pressure":
            return self.blood_pressure()
        if can_refuse and random.random() > self.observation_probability:
            refused = random.choice([True, False])
            if not refused:
                # missed observation, omit from set
                return []
            observation["patient_refused"] = refused
        else:
            observation["patient_refused"] = False
            observation_generator = getattr(self, observation_type)
            observation_data = observation_generator()
            if observation_data is None:
                return []
            observation.update(observation_data)
        return [observation]

    def generate_observation_set(self) -> Dict[str, Any]:
        observations = []
        for observation_type in OBSERVATION_TYPES:
            observations += self.generate_observation(observation_type)
        return {
            "record_time": datetime(),
            "score_system": score_system(self.score_system),
            "observations": observations,
            "is_partial": all(
                next(
                    (ob for ob in observations if ob["observation_type"] == ob_typ),
                    False,
                )
                for ob_typ in REQUIRED_OBS
            ),
        }


def score_system(score_system: Optional[str] = None) -> str:
    if score_system:
        return score_system
    return "news2"


class ObservationSetCreator(Protocol):
    def __call__(self) -> Dict[str, Any]:
        ...


def observation_set_factory(
    observation_probability: float = 0.98,
    trajectory: Trajectory = None,
    score_system: Optional[str] = None,
) -> ObservationSetCreator:
    def generate() -> Dict[str, Any]:
        generator = ObsSetGenerator(
            trajectory=trajectory or Trajectory.random_choice(),
            observation_probability=observation_probability,
            score_system=score_system,
        )
        return generator.generate_observation_set()

    return generate
