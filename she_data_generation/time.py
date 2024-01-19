import datetime as dt
import random


def datetime(days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0) -> str:
    value: dt.datetime = dt.datetime.utcnow() + dt.timedelta(
        days=days, hours=hours, minutes=minutes, seconds=seconds
    )
    return value.isoformat(timespec="milliseconds") + "Z"


def date(days: int = 0) -> str:
    value: dt.date = dt.date.today() + dt.timedelta(days=days)
    return value.isoformat()


def youngest_birthday(age: int, today: dt.date) -> dt.date:
    # The youngest person of the correct age has their birthday on the same month and day as today
    # except where today is 29th Feb and the target year is not a leap year in which case use 1st March
    birthday: dt.date = dt.date(today.year - age, today.month, 1) + dt.timedelta(
        days=today.day - 1
    )
    return birthday


def date_of_birth(min_age: int = 0, max_age: int = 99) -> str:
    today = dt.date.today()
    youngest = youngest_birthday(min_age, today)
    oldest = min(
        youngest_birthday(max_age + 1, today + dt.timedelta(days=1)),
        youngest_birthday(max_age + 1, today) + dt.timedelta(days=1),
    )

    # randint is an inclusive range
    chosen = random.randint(0, (youngest - oldest).days)
    birthday = oldest + dt.timedelta(chosen)

    return birthday.isoformat()
