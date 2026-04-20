from unittest import TestCase

from pit38.domain.stock.profit.per_stock_calculator import PerStockProfitCalculator
from tests.utils import StubExchanger, DateAwareExchanger, apple, usd, buy, sell, zl


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
        
    def test_regression(self):
        calculator = PerStockProfitCalculator(StubExchanger())
        transactions = [
            buy(apple(34.24657534), usd(1000), "2022-02-01 12:00"),
            buy(apple(127.388535), usd(4000), "2022-02-04 12:00"),
            sell(apple(161.6351104), usd(5500), "2022-03-01 12:00")
        ]
        
        profit = calculator.calculate_cost_and_income(transactions)

        self.assertEqual(profit.get_cost(2022), zl(20000))
        self.assertEqual(profit.get_income(2022), zl(22000))

    def test_partial_sell(self):
        calculator = PerStockProfitCalculator(StubExchanger())
        transactions = [
            buy(apple(10), usd(1000), "2020-01-01 12:00"),
            sell(apple(3), usd(400), "2020-06-01 12:00"),
        ]
        profit = calculator.calculate_cost_and_income(transactions)

        self.assertEqual(profit.get_cost(2020), zl(1200))
        self.assertEqual(profit.get_income(2020), zl(1600))

    def test_partial_sell_uses_buy_date_exchange_rate(self):
        exchanger = DateAwareExchanger({
            "2020-01": 4.0,
            "2020-06": 5.0,
        })
        calculator = PerStockProfitCalculator(exchanger)
        transactions = [
            buy(apple(10), usd(1000), "2020-01-15 12:00"),
            sell(apple(3), usd(400), "2020-06-15 12:00"),
        ]
        profit = calculator.calculate_cost_and_income(transactions)

        # cost: 3/10 * 1000 USD * 4.0 (BUY date rate) = 1200 PLN
        self.assertEqual(profit.get_cost(2020), zl(1200))
        # income: 400 USD * 5.0 (SELL date rate) = 2000 PLN
        self.assertEqual(profit.get_income(2020), zl(2000))

    def test_sell_without_buy_raises_error(self):
        calculator = PerStockProfitCalculator(StubExchanger())
        transactions = [
            sell(apple(1), usd(200), "2020-01-01 12:00"),
        ]
        with self.assertRaises(ValueError) as ctx:
            calculator.calculate_cost_and_income(transactions)
        self.assertIn("No buy transaction", str(ctx.exception))
