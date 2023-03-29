from unittest import TestCase

import pendulum

from domain.crypto.profit_calculator import YearlyProfitCalculator
from domain.currency_exchange_service.currencies import Currency, FiatValue
from domain.tax_service.profit_per_year import ProfitPerYear
from domain.transactions import Transaction, Action, AssetValue


class StubExchanger:
    def exchange(self, date: pendulum.DateTime, fiat_value: FiatValue) -> FiatValue:
        if fiat_value.currency == Currency.DOLLAR:
            return FiatValue(fiat_value.amount * 4.0, Currency.ZLOTY)
        return FiatValue(fiat_value.amount, Currency.ZLOTY)


class TestYearlyProfitCalculator(TestCase):
    @classmethod
    def _btc(cls, amount):
        return AssetValue(amount, "BTC")

    @classmethod
    def _usd(cls, amount):
        return FiatValue(amount, Currency.DOLLAR)

    @classmethod
    def _buy(cls, crypto, fiat, date):
        parsed_date = pendulum.parse(date)
        return Transaction(date=parsed_date, asset=crypto, fiat_value=fiat, action=Action.BUY)

    @classmethod
    def _sell(cls, crypto, fiat, date):
        parsed_date = pendulum.parse(date)
        return Transaction(date=parsed_date, asset=crypto, fiat_value=fiat, action=Action.SELL)

    def test_profit_per_year(self):
        transactions = [
            self._buy(self._btc(1), self._usd(100), date="2019-01-01"),
            self._sell(self._btc(1), self._usd(200), date="2019-01-02"),
            self._buy(self._btc(1), self._usd(200), date="2020-01-01"),
            self._sell(self._btc(1), self._usd(300), date="2020-01-02"),
            self._buy(self._btc(1), self._usd(250), date="2021-01-01"),
            self._sell(self._btc(1), self._usd(400), date="2021-01-02"),
        ]
        yearly_profit_calculator = YearlyProfitCalculator(StubExchanger())
        profit_per_year = yearly_profit_calculator.profit_per_year(transactions)
        expected_profit_per_year = ProfitPerYear(
            income={
                2019: FiatValue(800, Currency.ZLOTY),
                2020: FiatValue(1200, Currency.ZLOTY),
                2021: FiatValue(1600, Currency.ZLOTY)
            }, cost={
                2019: FiatValue(400, Currency.ZLOTY),
                2020: FiatValue(800, Currency.ZLOTY),
                2021: FiatValue(1000, Currency.ZLOTY)
            }
        )

        self.assertEqual(profit_per_year, expected_profit_per_year)
