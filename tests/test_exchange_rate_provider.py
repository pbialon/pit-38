from unittest import TestCase

import pendulum

from src.currency_exchange_service.exchange_rates_provider import ExchangeRatesProvider


class TestExchangeRatesProvider(TestCase):
    def test_get_rate(self):
        start_date = pendulum.date(2022, 1, 1)
        end_date = pendulum.date(2022, 12, 31)
        exchange_rates_provider = ExchangeRatesProvider(start_date, end_date)

        self.assertEqual(exchange_rates_provider.get_rate("USD", pendulum.date(2022, 1, 3)), 4.0424)
        self.assertEqual(exchange_rates_provider.get_rate("EUR", pendulum.date(2022, 12, 12)), 4.6912)
