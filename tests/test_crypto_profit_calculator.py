from unittest import TestCase

from pit38.domain.crypto.profit_calculator import YearlyProfitCalculator
from pit38.domain.tax_service.profit_per_year import ProfitPerYear
from tests.utils import buy, sell, btc, eth, usd, StubExchanger, zl


class TestYearlyProfitCalculator(TestCase):
    def test_profit_per_year(self):
        transactions = [
            buy(btc(1), usd(100), "2019-01-01"),
            sell(btc(1), usd(200), "2019-01-02"),
            buy(btc(1), usd(200), "2020-01-01"),
            sell(btc(1), usd(300), "2020-01-02"),
            buy(btc(1), usd(250), "2021-01-01"),
            sell(btc(1), usd(400), "2021-01-02"),
        ]
        yearly_profit_calculator = YearlyProfitCalculator(StubExchanger())
        profit_per_year = yearly_profit_calculator.profit_per_year(transactions)
        expected_profit_per_year = ProfitPerYear(
            income={
                2019: zl(800),
                2020: zl(1200),
                2021: zl(1600)
            }, cost={
                2019: zl(400),
                2020: zl(800),
                2021: zl(1000)
            }
        )

        self.assertEqual(profit_per_year, expected_profit_per_year)

    def test_buy_one_year_sell_next(self):
        transactions = [
            buy(btc(1), usd(100), "2020-01-01"),
            sell(btc(1), usd(300), "2021-06-01"),
        ]
        calculator = YearlyProfitCalculator(StubExchanger())
        profit = calculator.profit_per_year(transactions)

        self.assertEqual(profit.get_cost(2020), zl(400))
        self.assertEqual(profit.get_income(2020), zl(0))
        self.assertEqual(profit.get_cost(2021), zl(0))
        self.assertEqual(profit.get_income(2021), zl(1200))

    def test_buy_without_sell(self):
        transactions = [
            buy(btc(1), usd(100), "2020-01-01"),
            buy(btc(2), usd(500), "2020-06-01"),
        ]
        calculator = YearlyProfitCalculator(StubExchanger())
        profit = calculator.profit_per_year(transactions)

        self.assertEqual(profit.get_cost(2020), zl(2400))
        self.assertEqual(profit.get_income(2020), zl(0))

    def test_multiple_cryptocurrencies(self):
        transactions = [
            buy(btc(1), usd(100), "2020-01-01"),
            buy(eth(10), usd(200), "2020-01-02"),
            sell(btc(1), usd(300), "2020-06-01"),
            sell(eth(10), usd(500), "2020-06-02"),
        ]
        calculator = YearlyProfitCalculator(StubExchanger())
        profit = calculator.profit_per_year(transactions)

        self.assertEqual(profit.get_cost(2020), zl(1200))
        self.assertEqual(profit.get_income(2020), zl(3200))
