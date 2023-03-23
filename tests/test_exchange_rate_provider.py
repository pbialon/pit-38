from unittest import TestCase

import pendulum

from domain.currency_exchange_service.currencies import Currency
from domain.currency_exchange_service.exchange_rates_provider import ExchangeRatesProvider


class TestExchangeRatesProvider(TestCase):
    def test_get_rate(self):
        exchange_rates_provider = ExchangeRatesProvider()

        self.assertEqual(exchange_rates_provider.get_rate(Currency.DOLLAR, pendulum.date(2022, 1, 3)), 4.0424)
        self.assertEqual(exchange_rates_provider.get_rate(Currency.EURO, pendulum.date(2022, 12, 12)), 4.6912)
