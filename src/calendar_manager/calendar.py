import pendulum
import holidays

from src.utils import YEAR


class Calendar:
    def __init__(self):
        self.holidays = self._get_holidays()

    def is_out_of_range(self, day: pendulum.DateTime):
        return day < pendulum.datetime(YEAR, 1, 1)

    def is_workday(self, day: pendulum.DateTime):
        return not self._is_weekend(day) and not self._is_holiday(day)

    def _is_holiday(self, day: pendulum.DateTime):
        return day in self.holidays

    def _is_weekend(self, day: pendulum.DateTime):
        # Saturday or Sunday
        return day.format("E") in ("6", "7")

    def _get_holidays(self, year: int = YEAR) -> list:
        dates = holidays.Poland(years=year).values()
        return [pendulum.parse(str(date)) for date in dates]
