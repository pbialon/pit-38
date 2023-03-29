from unittest import TestCase

from domain.calendar_service.calendar import Calendar
from domain.currency_exchange_service.exchanger import Exchanger
from tests.utils import usd, zl, date, datetime


class ExchangeRateProviderStub:
    def get_rate(self, currency, date):
        return 4.0


class TestExchanger(TestCase):
    def test_get_day_one(self):
        exchanger = Exchanger(None, Calendar())

        day_one = exchanger.get_day_one(datetime("2022-01-04"))
        self.assertEqual(day_one, date("2022-01-03"))

        day_one = exchanger.get_day_one(datetime("2022-01-09"))
        self.assertEqual(day_one, date("2022-01-07"))

        day_one = exchanger.get_day_one(datetime("2022-01-10"))
        self.assertEqual(day_one, date("2022-01-07"))

        day_one = exchanger.get_day_one(datetime("2022-01-11"))
        self.assertEqual(day_one, date("2022-01-10"))

    def test_exchange(self):
        exchanger = Exchanger(ExchangeRateProviderStub(), Calendar())
        amount_in_pln = exchanger.exchange(datetime("2022-01-04"), usd(100))
        self.assertEqual(amount_in_pln, zl(400))

    def test_exchange_the_same_currency(self):
        exchanger = Exchanger(ExchangeRateProviderStub(), Calendar())
        amount_in_pln = exchanger.exchange(datetime("2022-01-04"), zl(100))
        self.assertEqual(amount_in_pln, zl(100))
