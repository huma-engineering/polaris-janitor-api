import random
import string
from typing import Protocol


def random_string(length: int, letters: bool = True, digits: bool = True) -> str:
    choices: str = ""
    if letters:
        choices += string.ascii_letters
    if digits:
        choices += string.digits
    return "".join(random.choice(choices) for _ in range(length))


class StringCreator(Protocol):
    def __call__(self, length: int) -> str:
        ...


def string_factory(letters: bool = True, digits: bool = True) -> StringCreator:
    def generate(length: int) -> str:
        return random_string(length=length, letters=letters, digits=digits)

    return generate


class SegmentedStringCreator(Protocol):
    def __call__(self, *segment_lengths: int) -> str:
        ...


def segmented_string_factory(
    letters: bool = True, digits: bool = True, splitter: str = "-"
) -> SegmentedStringCreator:
    factory = string_factory(letters=letters, digits=digits)

    def generate(*segment_lengths: int) -> str:
        return splitter.join((factory(length) for length in segment_lengths))

    return generate
