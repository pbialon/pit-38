from unittest import TestCase

from domain.currency_exchange_service.currencies import Currency
from domain.currency_exchange_service.exchange_rates_provider import ExchangeRatesProvider
from tests.utils import date


class TestExchangeRatesProvider(TestCase):
    def test_get_rate(self):
        exchange_rates_provider = ExchangeRatesProvider()

        self.assertEqual(exchange_rates_provider.get_rate(Currency.DOLLAR, date("2022-01-03")), 4.0424)
        self.assertEqual(exchange_rates_provider.get_rate(Currency.EURO, date("2022-12-12")), 4.6912)
