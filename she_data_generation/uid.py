from ._faker import faker


def uuid4() -> str:
    return faker.uuid4(cast_to=str)
