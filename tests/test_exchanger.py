from unittest import TestCase

import pendulum

from calendar_service.calendar import Calendar
from currency_exchange_service.exchanger import Exchanger


class TestExchanger(TestCase):
    def test_get_day_one(self):
        exchanger = Exchanger(None, Calendar())

        day_one = exchanger.get_day_one(pendulum.date(2022, 1, 4))
        self.assertEqual(day_one, pendulum.date(2022, 1, 3))

        day_one = exchanger.get_day_one(pendulum.date(2022, 1, 9))
        self.assertEqual(day_one, pendulum.date(2022, 1, 7))

        day_one = exchanger.get_day_one(pendulum.date(2022, 1, 10))
        self.assertEqual(day_one, pendulum.date(2022, 1, 7))

        day_one = exchanger.get_day_one(pendulum.date(2022, 1, 11))
        self.assertEqual(day_one, pendulum.date(2022, 1, 10))

    def test_exchange(self):
        class ExchangeRateProviderStub:
            def get_rate(self, currency, date):
                return 4.0

        exchanger = Exchanger(ExchangeRateProviderStub(), Calendar())
        self.assertEqual(exchanger.exchange(pendulum.date(2022, 1, 4), 100), 400)
