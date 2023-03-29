from typing import List
from unittest import TestCase

from domain.stock.operations.stock_split import StockSplit
from domain.stock.profit.profit_calculator import ProfitCalculator
from domain.tax_service.profit_per_year import ProfitPerYear
from domain.transactions import Transaction
from tests.utils import buy, apple, usd, sell, amazon, dividend, datetime, custody_fee, StubExchanger, zl


class TestProfitCalculator(TestCase):
    def test_calculate_profit_per_year(self):
        transactions = [
            buy(apple(1), usd(100), "2019-01-01 12:00"),
            buy(amazon(1), usd(1000), "2019-01-01 12:00"),
            sell(apple(20), usd(200), "2020-01-01 12:00"),
            sell(amazon(1), usd(2000), "2020-01-01 12:00"),
        ]
        dividends = [
            dividend(usd(1.0), "2019-01-01 12:00"),
            dividend(usd(4.0), "2019-01-01 12:00"),
        ]
        stock_splits = [
            StockSplit(datetime("2019-12-01 12:00"), "AAPL", 20),
        ]
        custody_fees = [
            custody_fee(usd(0.50), "2019-01-01 12:00"),
            custody_fee(usd(0.50), "2019-07-01 12:00"),
            custody_fee(usd(0.50), "2020-01-01 12:00"),
            custody_fee(usd(0.50), "2020-07-01 12:00"),
        ]

        per_stock_calculator = PerStockCalculatorStub({
            "AAPL": ProfitPerYear(
                cost={2019: zl(0), 2020: zl(400)},
                income={2019: zl(0), 2020: zl(800)},
            ), "AMZN": ProfitPerYear(
                cost={2019: zl(0), 2020: zl(4000)},
                income={2019: zl(0), 2020: zl(8000)},
            )
        })
        calculator = ProfitCalculator(StubExchanger(), per_stock_calculator)

        profit = calculator.calculate_cumulative_cost_and_income(
            transactions, stock_splits, dividends, custody_fees)

        expected_profit = ProfitPerYear(
            cost={2019: zl(4), 2020: zl(4404)},
            income={2019: zl(20), 2020: zl(8800)}
        )
        self.assertEqual(expected_profit, profit)


class PerStockCalculatorStub:
    def __init__(self, profit: dict[str, ProfitPerYear]):
        self.profit = profit

    def _company(self, transactions: List[Transaction]):
        return transactions[0].asset.asset_name

    def calculate_cost_and_income(self, transactions: List[Transaction]) -> ProfitPerYear:
        return self.profit[self._company(transactions)]
