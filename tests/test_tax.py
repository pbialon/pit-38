from unittest import TestCase

from domain.tax_service.profit_per_year import ProfitPerYear
from domain.tax_service.tax_calculator import TaxCalculator
from tests.utils import zl


class TestTaxCalculatorDeductions(TestCase):
    def test_deductible_loss_from_previous_years_no_loss_no_profit(self):
        tax_calculator = TaxCalculator()
        income = {2019: zl(100), 2020: zl(100), 2021: zl(200)}
        cost = {2019: zl(100), 2020: zl(100), 2021: zl(200)}
        profit = ProfitPerYear(income, cost)
        loss = tax_calculator.deductible_loss_from_previous_years(profit, 2021)
        self.assertEqual(zl(0), loss)

    def test_deductible_loss_from_previous_years_profit_only(self):
        tax_calculator = TaxCalculator()
        income = {2019: zl(200), 2020: zl(200), 2021: zl(200)}
        cost = {2019: zl(100), 2020: zl(100), 2021: zl(100)}
        profit = ProfitPerYear(income, cost)
        loss = tax_calculator.deductible_loss_from_previous_years(profit, 2021)
        self.assertEqual(zl(0), loss)

    def test_deductible_loss_from_previous_years_loss_only(self):
        tax_calculator = TaxCalculator()
        income = {2019: zl(100), 2020: zl(100), 2021: zl(100)}
        cost = {2019: zl(200), 2020: zl(200), 2021: zl(200)}
        profit = ProfitPerYear(income, cost)

        loss = tax_calculator.deductible_loss_from_previous_years(profit, 2021)
        self.assertEqual(zl(200), loss)

    def test_deductible_loss_from_previous_years_loss_and_profit(self):
        tax_calculator = TaxCalculator()
        income = {2019: zl(100), 2020: zl(150), 2021: zl(200)}
        cost = {2019: zl(200), 2020: zl(100), 2021: zl(100)}
        profit = ProfitPerYear(income, cost)

        loss = tax_calculator.deductible_loss_from_previous_years(profit, 2021)
        self.assertEqual(zl(50), loss)

    def test_deductible_loss_from_previous_years_deducted_some_in_previous_year(self):
        tax_calculator = TaxCalculator()
        # deducted 100 loss from 2018 in 2019
        income = {2018: zl(100), 2019: zl(400), 2020: zl(100), 2021: zl(200)}
        cost = {2018: zl(200), 2019: zl(200), 2020: zl(200), 2021: zl(100)}
        profit = ProfitPerYear(income, cost)

        loss = tax_calculator.deductible_loss_from_previous_years(profit, 2021)
        self.assertEqual(zl(100), loss)


class TestTaxCalculator(TestCase):
    def test_calculate_tax_per_year_sell_after_buy(self):
        tax_calculator = TaxCalculator()

        income = {2019: zl(200), 2020: zl(200), 2021: zl(200)}
        cost = {2019: zl(100), 2020: zl(100), 2021: zl(100)}
        profit = ProfitPerYear(income, cost)

        base_for_tax_2019 = tax_calculator.calculate_tax_per_year(profit, 2019).base_for_tax
        self.assertEqual(zl(100), base_for_tax_2019)

        base_for_tax_2020 = tax_calculator.calculate_tax_per_year(profit, 2020).base_for_tax
        self.assertEqual(zl(100), base_for_tax_2020)

        base_for_tax_2021 = tax_calculator.calculate_tax_per_year(profit, 2021).base_for_tax
        self.assertEqual(zl(100), base_for_tax_2021)

    def test_calculate_tax_per_year_hodl(self):
        tax_calculator = TaxCalculator()

        income = {2019: zl(0), 2020: zl(0), 2021: zl(1000)}
        cost = {2019: zl(100), 2020: zl(100), 2021: zl(100)}
        profit = ProfitPerYear(income, cost)

        base_for_tax_2019 = tax_calculator.calculate_tax_per_year(profit, 2019).base_for_tax
        self.assertEqual(zl(-100), base_for_tax_2019)

        base_for_tax_2020 = tax_calculator.calculate_tax_per_year(profit, 2020).base_for_tax
        self.assertEqual(zl(-200), base_for_tax_2020)

        base_for_tax_2021 = tax_calculator.calculate_tax_per_year(profit, 2021).base_for_tax
        self.assertEqual(zl(700), base_for_tax_2021)

    def test_calculate_tax_per_year_losses(self):
        tax_calculator = TaxCalculator()

        income = {2019: zl(50), 2020: zl(50), 2021: zl(500)}
        cost = {2019: zl(200), 2020: zl(200), 2021: zl(100)}
        profit = ProfitPerYear(income, cost)

        base_for_tax_2019 = tax_calculator.calculate_tax_per_year(profit, 2019).base_for_tax
        self.assertEqual(zl(-150), base_for_tax_2019)

        base_for_tax_2020 = tax_calculator.calculate_tax_per_year(profit, 2020).base_for_tax
        self.assertEqual(zl(-300), base_for_tax_2020)

        base_for_tax_2021 = tax_calculator.calculate_tax_per_year(profit, 2021).base_for_tax
        # 300 losses from previous years deducted
        self.assertEqual(zl(100), base_for_tax_2021)
