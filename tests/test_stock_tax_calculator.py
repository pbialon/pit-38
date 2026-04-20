from unittest import TestCase

from pit38.domain.tax_service.profit_per_year import ProfitPerYear
from pit38.domain.tax_service.stock_tax_calculator import StockTaxCalculator
from tests.utils import zl


class TestStockLossDeduction(TestCase):
    def test_loss_expired_after_5_years(self):
        calc = StockTaxCalculator()
        income = {2018: zl(100), 2025: zl(1000)}
        cost = {2018: zl(500), 2025: zl(100)}
        profit = ProfitPerYear(income, cost)

        result = calc.calculate_tax_per_year(profit, 2025)
        # Loss from 2018 expired (2025 - 2018 = 7 > 5)
        self.assertEqual(zl(0), result.deductible_loss)
        self.assertEqual(zl(900), result.base_for_tax)

    def test_loss_within_5_years(self):
        calc = StockTaxCalculator()
        income = {2021: zl(100), 2026: zl(1000)}
        cost = {2021: zl(500), 2026: zl(100)}
        profit = ProfitPerYear(income, cost)

        result = calc.calculate_tax_per_year(profit, 2026)
        # Loss from 2021: 400 PLN, within 5 years, post-2019 and <5M → full deduction
        self.assertEqual(zl(400), result.deductible_loss)
        self.assertEqual(zl(500), result.base_for_tax)

    def test_50_percent_cap_pre_2019_loss(self):
        calc = StockTaxCalculator()
        income = {2018: zl(0), 2019: zl(20000)}
        cost = {2018: zl(10000), 2019: zl(0)}
        profit = ProfitPerYear(income, cost)

        result = calc.calculate_tax_per_year(profit, 2019)
        # Loss from 2018: 10K, pre-2019 → 50% cap = max 5K deductible
        self.assertEqual(zl(5000), result.deductible_loss)
        self.assertEqual(zl(15000), result.base_for_tax)

    def test_post_2019_small_loss_full_deduction(self):
        calc = StockTaxCalculator()
        income = {2020: zl(0), 2021: zl(50000)}
        cost = {2020: zl(30000), 2021: zl(0)}
        profit = ProfitPerYear(income, cost)

        result = calc.calculate_tax_per_year(profit, 2021)
        # Loss from 2020: 30K, post-2019 and <5M → full deduction via one-time option
        self.assertEqual(zl(30000), result.deductible_loss)
        self.assertEqual(zl(20000), result.base_for_tax)

    def test_post_2019_large_loss_over_5m_capped(self):
        calc = StockTaxCalculator()
        income = {2020: zl(0), 2021: zl(10_000_000)}
        cost = {2020: zl(8_000_000), 2021: zl(0)}
        profit = ProfitPerYear(income, cost)

        result = calc.calculate_tax_per_year(profit, 2021)
        # Loss from 2020: 8M, post-2019 but >5M → 50% cap = max 4M
        self.assertEqual(zl(4_000_000), result.deductible_loss)
        self.assertEqual(zl(6_000_000), result.base_for_tax)

    def test_multiple_losses_each_has_own_cap(self):
        calc = StockTaxCalculator()
        income = {
            2020: zl(0),
            2021: zl(0),
            2023: zl(100_000),
        }
        cost = {
            2020: zl(10_000),
            2021: zl(20_000),
            2023: zl(0),
        }
        profit = ProfitPerYear(income, cost)

        result = calc.calculate_tax_per_year(profit, 2023)
        # Loss 2020: 10K (post-2019, <5M → full 10K)
        # Loss 2021: 20K (post-2019, <5M → full 20K)
        # Total: 30K
        self.assertEqual(zl(30_000), result.deductible_loss)
        self.assertEqual(zl(70_000), result.base_for_tax)

    def test_mixed_expired_and_valid_losses(self):
        calc = StockTaxCalculator()
        income = {
            2019: zl(0),
            2022: zl(0),
            2026: zl(10_000),
        }
        cost = {
            2019: zl(5000),
            2022: zl(3000),
            2026: zl(0),
        }
        profit = ProfitPerYear(income, cost)

        result = calc.calculate_tax_per_year(profit, 2026)
        # Loss from 2019: expired (2026 - 2019 = 7 > 5)
        # Loss from 2022: 3K, valid, post-2019 → full deduction
        self.assertEqual(zl(3000), result.deductible_loss)
        self.assertEqual(zl(7000), result.base_for_tax)

    def test_no_deduction_in_loss_year(self):
        calc = StockTaxCalculator()
        income = {2023: zl(100)}
        cost = {2023: zl(500)}
        profit = ProfitPerYear(income, cost)

        result = calc.calculate_tax_per_year(profit, 2023)
        self.assertEqual(zl(0), result.deductible_loss)
        self.assertEqual(zl(-400), result.base_for_tax)
        self.assertEqual(zl(0), result.tax)

    def test_deduction_capped_by_profit(self):
        calc = StockTaxCalculator()
        income = {2020: zl(0), 2021: zl(500)}
        cost = {2020: zl(10000), 2021: zl(0)}
        profit = ProfitPerYear(income, cost)

        result = calc.calculate_tax_per_year(profit, 2021)
        # Loss 10K but profit only 500 → deduct only 500
        self.assertEqual(zl(500), result.deductible_loss)
        self.assertEqual(zl(0), result.base_for_tax)
        self.assertEqual(zl(0), result.tax)

    def test_manual_deductible_loss_override(self):
        calc = StockTaxCalculator()
        income = {2020: zl(100), 2021: zl(1000)}
        cost = {2020: zl(200), 2021: zl(100)}
        profit = ProfitPerYear(income, cost)

        result = calc.calculate_tax_per_year(profit, 2021, deductible_loss=500)
        self.assertEqual(zl(500), result.deductible_loss)
        self.assertEqual(zl(400), result.base_for_tax)
        self.assertEqual(zl(76), result.tax)

    def test_tax_19_percent(self):
        calc = StockTaxCalculator()
        income = {2023: zl(1000)}
        cost = {2023: zl(0)}
        profit = ProfitPerYear(income, cost)

        result = calc.calculate_tax_per_year(profit, 2023)
        self.assertEqual(zl(1000), result.base_for_tax)
        self.assertEqual(zl(190), result.tax)
