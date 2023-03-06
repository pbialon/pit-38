from unittest import TestCase

import pendulum

from domain.calendar_service.calendar import Calendar


class TestCalendar(TestCase):
    def test_is_workday(self):
        calendar = Calendar()
        self.assertTrue(calendar.is_workday(pendulum.date(2022, 1, 3)))
        self.assertFalse(calendar.is_workday(pendulum.date(2022, 1, 2)))
        self.assertFalse(calendar.is_workday(pendulum.date(2022, 11, 1)))
