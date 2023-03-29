from unittest import TestCase

import pendulum

from domain.calendar_service.calendar import Calendar
from domain.currency_exchange_service.currencies import FiatValue, Currency
from domain.currency_exchange_service.exchanger import Exchanger
from tests.utils import usd, zl


class ExchangeRateProviderStub:
    def get_rate(self, currency, date):
        return 4.0


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
        exchanger = Exchanger(ExchangeRateProviderStub(), Calendar())
        amount = usd(100)
        amount_in_pln = exchanger.exchange(pendulum.date(2022, 1, 4), amount)
        self.assertEqual(amount_in_pln, zl(400))

    def test_exchange_the_same_currency(self):
        exchanger = Exchanger(ExchangeRateProviderStub(), Calendar())
        amount = zl(100)
        amount_in_pln = exchanger.exchange(pendulum.date(2022, 1, 4), amount)
        self.assertEqual(amount_in_pln, zl(100))
