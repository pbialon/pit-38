from unittest import TestCase

import pendulum

from domain.stock.operations.stock_split import StockSplit
from domain.stock.stock_split_handler import StockSplitHandler


class TestStockSplitHandler(TestCase):
    def test_multiplier_for_date(self):
        stock_splits = [
            StockSplit(date=pendulum.datetime(2020, 1, 1), stock="AAPL", ratio=10),
            StockSplit(date=pendulum.datetime(2021, 1, 1), stock="AAPL", ratio=10),
            StockSplit(date=pendulum.datetime(2022, 1, 1), stock="AAPL", ratio=10),
        ]

        self.assertEqual(
            StockSplitHandler.multiplier_for_date(stock_splits, pendulum.datetime(2019, 1, 1)), 1000
        )
        self.assertEqual(
            StockSplitHandler.multiplier_for_date(stock_splits, pendulum.datetime(2020, 1, 1)), 100
        )
        self.assertEqual(
            StockSplitHandler.multiplier_for_date(stock_splits, pendulum.datetime(2021, 1, 1)), 10
        )
        self.assertEqual(
            StockSplitHandler.multiplier_for_date(stock_splits, pendulum.datetime(2022, 1, 1)), 1
        )
