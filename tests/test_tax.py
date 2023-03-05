from unittest import TestCase

import pendulum

from currency_exchange_service.currencies import FiatValue
from domain.crypto.profit_calculator import YearlyProfitCalculator
from domain.crypto.tax import TaxCalculator
from domain.crypto.transaction import CryptoValue, Transaction, Action


class StubExchanger:
    def exchange(self, date, fiat_value):
        return fiat_value


yearly_profit_calculator = YearlyProfitCalculator(StubExchanger())


class TestTaxCalculatorDeductions(TestCase):
    def test_deductable_loss_from_previous_years_no_loss_no_profit(self):
        tax_calculator = TaxCalculator(yearly_profit_calculator)
        income = {2019: 100, 2020: 100, 2021: 200}
        cost = {2019: 100, 2020: 100, 2021: 200}
        tax = tax_calculator.deductable_loss_from_previous_years(income, cost, 2021)
        self.assertEqual(0, tax)

    def test_deductable_loss_from_previous_years_profit_only(self):
        tax_calculator = TaxCalculator(yearly_profit_calculator)
        income = {2019: 200, 2020: 200, 2021: 200}
        cost = {2019: 100, 2020: 100, 2021: 100}
        tax = tax_calculator.deductable_loss_from_previous_years(income, cost, 2021)
        self.assertEqual(0, tax)

    def test_deductable_loss_from_previous_years_loss_only(self):
        tax_calculator = TaxCalculator(yearly_profit_calculator)
        income = {2019: 100, 2020: 100, 2021: 100}
        cost = {2019: 200, 2020: 200, 2021: 200}
        tax = tax_calculator.deductable_loss_from_previous_years(income, cost, 2021)
        self.assertEqual(200, tax)

    def test_deductable_loss_from_previous_years_loss_and_profit(self):
        tax_calculator = TaxCalculator(yearly_profit_calculator)
        income = {2019: 100, 2020: 150, 2021: 200}
        cost = {2019: 200, 2020: 100, 2021: 100}
        tax = tax_calculator.deductable_loss_from_previous_years(income, cost, 2021)
        self.assertEqual(50, tax)

    def test_deductable_loss_from_previous_years_deducted_some_in_previous_year(self):
        tax_calculator = TaxCalculator(yearly_profit_calculator)
        # deducted 100 loss from 2018 in 2019
        income = {2018: 100, 2019: 400, 2020: 100, 2021: 200}
        cost = {2018: 200, 2019: 200, 2020: 200, 2021: 100}
        tax = tax_calculator.deductable_loss_from_previous_years(income, cost, 2021)
        self.assertEqual(100, tax)


class TestTaxCalculator(TestCase):

    def _crypto(self, amount):
        return CryptoValue(amount, "BTC")

    def _fiat(self, amount):
        return FiatValue(amount, "EUR")

    def _buy(self, crypto, fiat, date):
        parsed_date = pendulum.parse(date)
        return Transaction(date=parsed_date, crypto_value=crypto, fiat_value=fiat, action=Action.BUY)

    def _sell(self, crypto, fiat, date):
        parsed_date = pendulum.parse(date)
        return Transaction(date=parsed_date, crypto_value=crypto, fiat_value=fiat, action=Action.SELL)

    def test_calculate_tax_per_year_sell_after_buy(self):
        tax_calculator = TaxCalculator(yearly_profit_calculator)
        transactions = [
            self._buy(self._crypto(1), self._fiat(100), date="2019-01-01"),
            self._sell(self._crypto(1), self._fiat(200), date="2019-01-02"),
            self._buy(self._crypto(1), self._fiat(100), date="2020-01-01"),
            self._sell(self._crypto(1), self._fiat(200), date="2020-01-02"),
            self._buy(self._crypto(1), self._fiat(100), date="2021-01-01"),
            self._sell(self._crypto(1), self._fiat(200), date="2021-01-02"),
        ]
        tax_2019 = tax_calculator.calculate_tax_per_year(transactions, 2019)
        self.assertEqual(19, tax_2019)

        tax_2020 = tax_calculator.calculate_tax_per_year(transactions, 2020)
        self.assertEqual(19, tax_2020)

        tax_2021 = tax_calculator.calculate_tax_per_year(transactions, 2021)
        self.assertEqual(19, tax_2021)

    def test_calculate_tax_per_year_hodl(self):
        tax_calculator = TaxCalculator(yearly_profit_calculator)
        transactions = [
            self._buy(self._crypto(1), self._fiat(100), date="2019-01-01"),
            self._buy(self._crypto(1), self._fiat(100), date="2020-01-01"),
            self._buy(self._crypto(1), self._fiat(100), date="2021-01-01"),
            self._sell(self._crypto(3), self._fiat(1000), date="2021-01-02"),
        ]

        tax_2019 = tax_calculator.calculate_tax_per_year(transactions, 2019)
        self.assertEqual(0, tax_2019)

        tax_2020 = tax_calculator.calculate_tax_per_year(transactions, 2020)
        self.assertEqual(0, tax_2020)

        tax_2021 = tax_calculator.calculate_tax_per_year(transactions, 2021)
        self.assertEqual(700 * 0.19, tax_2021)

    def test_calculate_tax_per_year_losses(self):
        tax_calculator = TaxCalculator(yearly_profit_calculator)
        transactions = [
            self._buy(self._crypto(1), self._fiat(200), date="2019-01-01"),
            self._sell(self._crypto(1), self._fiat(50), date="2019-01-02"),
            self._buy(self._crypto(1), self._fiat(200), date="2020-01-01"),
            self._sell(self._crypto(1), self._fiat(50), date="2020-01-02"),
            self._buy(self._crypto(1), self._fiat(100), date="2021-01-01"),
            self._sell(self._crypto(1), self._fiat(500), date="2021-01-02"),
        ]

        tax_2019 = tax_calculator.calculate_tax_per_year(transactions, 2019)
        self.assertEqual(0, tax_2019)

        tax_2020 = tax_calculator.calculate_tax_per_year(transactions, 2020)
        self.assertEqual(0, tax_2020)

        tax_2021 = tax_calculator.calculate_tax_per_year(transactions, 2021)
        # 300 losses from previous years deducted
        self.assertEqual(19, tax_2021)
