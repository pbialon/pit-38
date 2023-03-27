from unittest import TestCase

import pendulum

from domain.crypto.profit_calculator import YearlyProfitCalculator
from domain.currency_exchange_service.currencies import Currency, FiatValue
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

    @classmethod
    def transaction_list(cls):
        return [
            cls._buy(cls._btc(1), cls._usd(100), date="2019-01-01"),
            cls._sell(cls._btc(1), cls._usd(200), date="2019-01-02"),
            cls._buy(cls._btc(1), cls._usd(200), date="2020-01-01"),
            cls._sell(cls._btc(1), cls._usd(300), date="2020-01-02"),
            cls._buy(cls._btc(1), cls._usd(250), date="2021-01-01"),
            cls._sell(cls._btc(1), cls._usd(400), date="2021-01-02"),
        ]

    def test_income_per_year(self):
        transactions = self.transaction_list()
        yearly_profit_calculator = YearlyProfitCalculator(StubExchanger())
        income_per_year = yearly_profit_calculator.income_per_year(transactions)
        self.assertEqual(income_per_year[2019], FiatValue(800, Currency.ZLOTY))
        self.assertEqual(income_per_year[2020], FiatValue(1200, Currency.ZLOTY))
        self.assertEqual(income_per_year[2021], FiatValue(1600, Currency.ZLOTY))

    def test_cost_per_year(self):
        transactions = self.transaction_list()
        yearly_profit_calculator = YearlyProfitCalculator(StubExchanger())
        cost_per_year = yearly_profit_calculator.cost_per_year(transactions)
        self.assertEqual(cost_per_year[2019], FiatValue(400, Currency.ZLOTY))
        self.assertEqual(cost_per_year[2020], FiatValue(800, Currency.ZLOTY))
        self.assertEqual(cost_per_year[2021], FiatValue(1000, Currency.ZLOTY))