from unittest import TestCase

import pendulum

from calendar_service.calendar import Calendar
from currency_exchange_service.currencies import FiatValue, Currency
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
        amount = FiatValue(100, Currency.DOLLAR)
        amount_in_pln = exchanger.exchange(pendulum.date(2022, 1, 4), amount)
        self.assertEqual(amount_in_pln.currency, Currency.ZLOTY)
        self.assertEqual(amount_in_pln.amount, 400)

    def test_exchange_the_same_currency(self):
        class ExchangeRateProviderStub:
            def get_rate(self, currency, date):
                return 4.0

        exchanger = Exchanger(ExchangeRateProviderStub(), Calendar())
        amount = FiatValue(100, Currency.ZLOTY)
        amount_in_pln = exchanger.exchange(pendulum.date(2022, 1, 4), amount)
        self.assertEqual(amount_in_pln.currency, Currency.ZLOTY)
        self.assertEqual(amount_in_pln.amount, 100)
