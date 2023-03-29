from unittest import TestCase

from domain.currency_exchange_service.currencies import FiatValue
from domain.tax_service.profit_per_year import ProfitPerYear


class TestProfitPerYear(TestCase):
    def test_add_income(self):
        profit = ProfitPerYear()
        profit.add_income(2020, FiatValue(100))
        profit.add_income(2020, FiatValue(100))

        self.assertEqual(profit.get_income(2020), FiatValue(200))

    def test_add_cost(self):
        profit = ProfitPerYear()
        profit.add_cost(2020, FiatValue(100))
        profit.add_cost(2020, FiatValue(100))

        self.assertEqual(profit.get_cost(2020), FiatValue(200))

    def test_get_profit(self):
        profit = ProfitPerYear()
        profit.add_income(2020, FiatValue(100))
        profit.add_cost(2020, FiatValue(50))

        self.assertEqual(profit.get_profit(2020), FiatValue(50))

    def test_add(self):
        profit1 = ProfitPerYear()
        profit1.add_income(2020, FiatValue(100))
        profit1.add_cost(2020, FiatValue(50))

        profit2 = ProfitPerYear()
        profit2.add_income(2020, FiatValue(100))
        profit2.add_cost(2020, FiatValue(50))

        profit3 = profit1 + profit2

        self.assertEqual(profit3.get_income(2020), FiatValue(200))
        self.assertEqual(profit3.get_cost(2020), FiatValue(100))
