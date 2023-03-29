from unittest import TestCase

from domain.calendar_service.calendar import Calendar
from tests.utils import date


class TestCalendar(TestCase):
    def test_is_workday(self):
        calendar = Calendar()
        self.assertTrue(calendar.is_workday(date("2022-01-03")))
        self.assertFalse(calendar.is_workday(date("2022-01-02")))
        self.assertFalse(calendar.is_workday(date("2022-11-01")))
