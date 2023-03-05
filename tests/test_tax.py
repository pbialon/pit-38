from unittest import TestCase

from domain.crypto.tax import TaxCalculator


class StubExchanger:
    def exchange(self, date, fiat_value):
        return fiat_value


class TestTaxCalculator(TestCase):
    def test_deductable_loss_from_previous_years_no_loss_no_profit(self):
        tax_calculator = TaxCalculator(StubExchanger())
        income = {2019: 100, 2020: 100, 2021: 200}
        cost = {2019: 100, 2020: 100, 2021: 200}
        tax = tax_calculator.deductable_loss_from_previous_years(income, cost, 2021)
        self.assertEqual(0, tax)

    def test_deductable_loss_from_previous_years_profit_only(self):
        tax_calculator = TaxCalculator(StubExchanger())
        income = {2019: 200, 2020: 200, 2021: 200}
        cost = {2019: 100, 2020: 100, 2021: 100}
        tax = tax_calculator.deductable_loss_from_previous_years(income, cost, 2021)
        self.assertEqual(0, tax)

    def test_deductable_loss_from_previous_years_loss_only(self):
        tax_calculator = TaxCalculator(StubExchanger())
        income = {2019: 100, 2020: 100, 2021: 100}
        cost = {2019: 200, 2020: 200, 2021: 200}
        tax = tax_calculator.deductable_loss_from_previous_years(income, cost, 2021)
        self.assertEqual(200, tax)

    def test_deductable_loss_from_previous_years_loss_and_profit(self):
        tax_calculator = TaxCalculator(StubExchanger())
        income = {2019: 100, 2020: 150, 2021: 200}
        cost = {2019: 200, 2020: 100, 2021: 100}
        tax = tax_calculator.deductable_loss_from_previous_years(income, cost, 2021)
        self.assertEqual(50, tax)

    def test_deductable_loss_from_previous_years_deducted_some_in_previous_year(self):
        tax_calculator = TaxCalculator(StubExchanger())
        # deducted 100 loss from 2018 in 2019
        income = {2018: 100, 2019: 400, 2020: 100, 2021: 200}
        cost = {2018: 200, 2019: 200, 2020: 200, 2021: 100}
        tax = tax_calculator.deductable_loss_from_previous_years(income, cost, 2021)
        self.assertEqual(100, tax)

    def calculate_tax_per_year(self):
        pass
