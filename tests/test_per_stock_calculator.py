from unittest import TestCase

import pendulum

from domain.currency_exchange_service.currencies import FiatValue, Currency
from domain.stock.profit.per_stock_calculator import PerStockProfitCalculator


class StubExchanger:
    def exchange(self, date: pendulum.DateTime, fiat_value: FiatValue) -> FiatValue:
        if fiat_value.currency == Currency.DOLLAR:
            return FiatValue(fiat_value.amount * 4.0, Currency.ZLOTY)
        return FiatValue(fiat_value.amount, Currency.ZLOTY)


class TestPerStockProfitCalculator(TestCase):
    def test_only_purchases(self):
        calculator = PerStockProfitCalculator(StubExchanger())
