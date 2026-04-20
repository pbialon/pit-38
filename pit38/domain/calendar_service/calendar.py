from typing import Iterable, List

import pendulum
import holidays


def current_year():
    return pendulum.now().year


def previous_year():
    return pendulum.now().year - 1


def year_start(year: int):
    return pendulum.date(year, 1, 1)


def year_end(year: int):
    return pendulum.date(year, 12, 31)


def yesterday() -> pendulum.Date:
    yesterday = pendulum.yesterday()
    return pendulum.date(yesterday.year, yesterday.month, yesterday.day)


class Calendar:
    YEARS_BACK = 5

    def __init__(self, year: int = current_year()):
        self.start_year = year - self.YEARS_BACK
        years = range(self.start_year, year + 1)
        self.holidays = self._get_holidays(years)

    def is_out_of_range(self, day: pendulum.Date):
        return day < pendulum.date(self.start_year, 1, 1)

    def is_workday(self, day: pendulum.DateTime) -> bool:
        return not self._is_weekend(day) and not self._is_holiday(day)

    def _is_holiday(self, day: pendulum.DateTime) -> bool:
        return day in self.holidays

    def _is_weekend(self, day: pendulum.DateTime) -> bool:
        # Saturday or Sunday
        return day.format("E") in ("6", "7")

    def _get_holidays(self, years: Iterable[int]) -> List[pendulum.Date]:
        dates = holidays.Poland(years=years).keys()
        return [pendulum.parse(str(date)).date() for date in dates]
