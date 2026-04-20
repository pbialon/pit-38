from unittest import TestCase

from pit38.domain.tax_service.profit_per_year import ProfitPerYear
from pit38.domain.tax_service.crypto_tax_calculator import CryptoTaxCalculator
from tests.utils import zl


class TestCryptoTaxCalculator(TestCase):
    def test_unlimited_loss_carryforward(self):
        calc = CryptoTaxCalculator()
        income = {2018: zl(100), 2025: zl(1000)}
        cost = {2018: zl(500), 2025: zl(100)}
        profit = ProfitPerYear(income, cost)

        result = calc.calculate_tax_per_year(profit, 2025)
        # Crypto: no 5-year limit, full 400 PLN deduction even after 7 years
        self.assertEqual(zl(400), result.deductible_loss)
        self.assertEqual(zl(500), result.base_for_tax)

    def test_no_50_percent_cap(self):
        calc = CryptoTaxCalculator()
        income = {2020: zl(0), 2021: zl(50000)}
        cost = {2020: zl(30000), 2021: zl(0)}
        profit = ProfitPerYear(income, cost)

        result = calc.calculate_tax_per_year(profit, 2021)
        # Crypto: no 50% cap, full 30K deducted
        self.assertEqual(zl(30000), result.deductible_loss)
        self.assertEqual(zl(20000), result.base_for_tax)

    def test_accumulated_losses_across_years(self):
        calc = CryptoTaxCalculator()
        income = {2019: zl(100), 2020: zl(100), 2021: zl(200)}
        cost = {2019: zl(200), 2020: zl(200), 2021: zl(200)}
        profit = ProfitPerYear(income, cost)

        result = calc.calculate_tax_per_year(profit, 2021)
        self.assertEqual(zl(200), result.deductible_loss)

    def test_loss_absorbed_by_intermediate_profit(self):
        calc = CryptoTaxCalculator()
        income = {2019: zl(100), 2020: zl(400), 2021: zl(200)}
        cost = {2019: zl(200), 2020: zl(100), 2021: zl(100)}
        profit = ProfitPerYear(income, cost)

        result = calc.calculate_tax_per_year(profit, 2021)
        # 2019: loss 100, 2020: profit 300 absorbs 100 loss, no loss left
        self.assertEqual(zl(0), result.deductible_loss)

    def test_tax_is_zero_when_loss(self):
        calc = CryptoTaxCalculator()
        income = {2021: zl(100)}
        cost = {2021: zl(500)}
        profit = ProfitPerYear(income, cost)

        result = calc.calculate_tax_per_year(profit, 2021)
        self.assertEqual(zl(0), result.tax)

    def test_manual_override(self):
        calc = CryptoTaxCalculator()
        income = {2021: zl(1000)}
        cost = {2021: zl(100)}
        profit = ProfitPerYear(income, cost)

        result = calc.calculate_tax_per_year(profit, 2021, deductible_loss=500)
        self.assertEqual(zl(500), result.deductible_loss)
        self.assertEqual(zl(400), result.base_for_tax)
