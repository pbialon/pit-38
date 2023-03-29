from unittest import TestCase

from domain.stock.profit.per_stock_calculator import PerStockProfitCalculator
from tests.utils import StubExchanger, apple, usd, buy, sell, zl


class TestPerStockProfitCalculator(TestCase):
    def test_only_purchases(self):
        calculator = PerStockProfitCalculator(StubExchanger())
        transactions = [
            buy(apple(1), usd(100), "2020-01-01 12:00"),
            buy(apple(10), usd(100), "2020-11-01 12:00"),
        ]
        profit = calculator.calculate_cost_and_income(transactions)

        self.assertEqual(profit.get_cost(2020), zl(0))
        self.assertEqual(profit.get_income(2020), zl(0))

    def test_sell_the_same_year(self):
        calculator = PerStockProfitCalculator(StubExchanger())
        transactions = [
            buy(apple(1), usd(100), "2020-01-01 12:00"),
            sell(apple(1), usd(200), "2020-02-01 12:00"),
        ]
        profit = calculator.calculate_cost_and_income(transactions)

        self.assertEqual(profit.get_cost(2020), zl(400))
        self.assertEqual(profit.get_income(2020), zl(800))

    def test_sell_next_year(self):
        calculator = PerStockProfitCalculator(StubExchanger())
        transactions = [
            buy(apple(1), usd(100), "2020-01-01 12:00"),
            sell(apple(1), usd(200), "2021-02-01 12:00"),
        ]
        profit = calculator.calculate_cost_and_income(transactions)

        self.assertEqual(profit.get_cost(2020), zl(0))
        self.assertEqual(profit.get_income(2020), zl(0))

        self.assertEqual(profit.get_cost(2021), zl(400))
        self.assertEqual(profit.get_income(2021), zl(800))

    def test_sell_next_year_and_buy(self):
        calculator = PerStockProfitCalculator(StubExchanger())
        transactions = [
            buy(apple(1), usd(100), "2020-01-01 12:00"),
            sell(apple(1), usd(200), "2021-02-01 12:00"),
            buy(apple(1), usd(100), "2021-03-01 12:00"),
        ]
        profit = calculator.calculate_cost_and_income(transactions)

        self.assertEqual(profit.get_cost(2020), zl(0))
        self.assertEqual(profit.get_income(2020), zl(0))

        self.assertEqual(profit.get_cost(2021), zl(400))
        self.assertEqual(profit.get_income(2021), zl(800))

    def test_multiple_buys(self):
        calculator = PerStockProfitCalculator(StubExchanger())
        transactions = [
            buy(apple(1), usd(100), "2020-01-01 12:00"),
            buy(apple(1), usd(100), "2020-02-01 12:00"),
            buy(apple(1), usd(100), "2020-03-01 12:00"),
            sell(apple(3), usd(200), "2020-12-01 12:00"),
        ]
        profit = calculator.calculate_cost_and_income(transactions)

        self.assertEqual(profit.get_cost(2020), zl(1200))
        self.assertEqual(profit.get_income(2020), zl(800))

    def test_multiple_buys_and_sells(self):
        calculator = PerStockProfitCalculator(StubExchanger())
        transactions = [
            buy(apple(1), usd(100), "2020-01-01 12:00"),
            buy(apple(1), usd(100), "2020-02-01 12:00"),
            buy(apple(1), usd(100), "2020-03-01 12:00"),
            sell(apple(1), usd(200), "2020-04-01 12:00"),
            # 2021
            buy(apple(1), usd(50), "2021-01-01 12:00"),
            sell(apple(3), usd(200), "2021-02-01 12:00"),
        ]
        profit = calculator.calculate_cost_and_income(transactions)

        self.assertEqual(profit.get_cost(2020), zl(400))
        self.assertEqual(profit.get_income(2020), zl(800))

        self.assertEqual(profit.get_cost(2021), zl(1000))
        self.assertEqual(profit.get_income(2021), zl(800))