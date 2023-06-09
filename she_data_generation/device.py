from typing import Any, Dict, Protocol

from she_data_generation.string import segmented_string_factory

from .uid import uuid4


class DeviceCreator(Protocol):
    def __call__(self) -> Dict[str, Any]:
        ...


def device_factory(location_id: str = None) -> DeviceCreator:
    def generate() -> Dict[str, Any]:
        string_gen = segmented_string_factory(letters=True, digits=True, splitter=" ")
        string = string_gen(4, 4, 2)
        return {
            "description": string,
            "location_id": location_id or uuid4(),
        }

    return generate
