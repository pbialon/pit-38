import pendulum

YEAR = 2022


def first_day_of_year(year: int = YEAR) -> pendulum.DateTime:
    return pendulum.datetime(year, 1, 1)


class InvalidYearException(Exception):
    pass
