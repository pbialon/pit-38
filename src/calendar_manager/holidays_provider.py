import pendulum
import holidays

YEAR = 2022


def get_holidays(year: int = YEAR) -> list:
    dates = holidays.Poland(years=year).values()
    return [pendulum.parse(str(date)) for date in dates]
