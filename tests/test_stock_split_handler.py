from unittest import TestCase


from domain.stock.operations.stock_split import StockSplit
from domain.stock.profit.stock_split_handler import StockSplitHandler
from tests.utils import usd, datetime, buy, apple, sell


class TestStockSplitHandler(TestCase):
    STOCK_SPLITS = [
        StockSplit(date=datetime("2020-01-01 11:00"), stock="AAPL", ratio=10),
        StockSplit(date=datetime("2021-01-01 11:00"), stock="AAPL", ratio=10),
        StockSplit(date=datetime("2022-01-01 11:00"), stock="AAPL", ratio=10),
    ]

    def test_multiplier_for_date(self):
        self.assertEqual(
            StockSplitHandler.multiplier_for_date(self.STOCK_SPLITS, datetime("2019-01-01 12:00")), 1000
        )

        self.assertEqual(
            StockSplitHandler.multiplier_for_date(self.STOCK_SPLITS, datetime("2020-01-01 10:00")), 1000
        )
        self.assertEqual(
            StockSplitHandler.multiplier_for_date(self.STOCK_SPLITS, datetime("2020-01-01 12:00")), 100
        )

        self.assertEqual(
            StockSplitHandler.multiplier_for_date(self.STOCK_SPLITS, datetime("2021-01-01 10:00")), 100
        )
        self.assertEqual(
            StockSplitHandler.multiplier_for_date(self.STOCK_SPLITS, datetime("2021-01-01 12:00")), 10
        )

        self.assertEqual(
            StockSplitHandler.multiplier_for_date(self.STOCK_SPLITS, datetime("2022-01-01 10:00")), 10
        )
        self.assertEqual(
            StockSplitHandler.multiplier_for_date(self.STOCK_SPLITS, datetime("2022-01-01 12:00")), 1
        )

    def test_incorporate_stock_splits_into_transactions(self):
        transactions = [
            buy(apple(1), usd(100), "2019-01-01 12:00"),
            buy(apple(10), usd(100), "2020-01-01 12:00"),
            sell(apple(100), usd(100), "2021-01-01 12:00"),
            sell(apple(1000), usd(100), "2022-01-01 12:00"),
        ]

        new_transactions = StockSplitHandler.incorporate_stock_splits_into_transactions(
            transactions, self.STOCK_SPLITS)

        expected_transactions = [
            buy(apple(1000), usd(100), "2019-01-01 12:00"),
            buy(apple(1000), usd(100), "2020-01-01 12:00"),
            sell(apple(1000), usd(100), "2021-01-01 12:00"),
            sell(apple(1000), usd(100), "2022-01-01 12:00"),
        ]
        self.assertListEqual(new_transactions, expected_transactions)
