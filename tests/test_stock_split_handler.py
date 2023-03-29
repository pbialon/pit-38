from unittest import TestCase

import pendulum

from domain.currency_exchange_service.currencies import Currency, FiatValue
from domain.stock.operations.stock_split import StockSplit
from domain.stock.stock_split_handler import StockSplitHandler
from domain.transactions import AssetValue, Transaction, Action


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

    def test_incorporate_stock_splits_into_transactions(self):
        stock_splits = [
            StockSplit(date=pendulum.datetime(2020, 1, 1), stock="AAPL", ratio=10),
            StockSplit(date=pendulum.datetime(2021, 1, 1), stock="AAPL", ratio=10),
            StockSplit(date=pendulum.datetime(2022, 1, 1), stock="AAPL", ratio=10),
        ]

        transactions = [
            Transaction(date=pendulum.datetime(2019, 1, 1),
                        action=Action.BUY,
                        asset=AssetValue(1, "AAPL"),
                        fiat_value=FiatValue(100, Currency.DOLLAR)),
            Transaction(date=pendulum.datetime(2020, 1, 1),
                        action=Action.BUY,
                        asset=AssetValue(10, "AAPL"),
                        fiat_value=FiatValue(100, Currency.DOLLAR)),
            Transaction(date=pendulum.datetime(2021, 1, 1),
                        action=Action.SELL,
                        asset=AssetValue(100, "AAPL"),
                        fiat_value=FiatValue(100, Currency.DOLLAR)),
            Transaction(date=pendulum.datetime(2022, 1, 1),
                        action=Action.SELL,
                        asset=AssetValue(1000, "AAPL"),
                        fiat_value=FiatValue(100, Currency.DOLLAR)),
        ]

        new_transactions = StockSplitHandler.incorporate_stock_splits_into_transactions(transactions, stock_splits)
        expected_transactions = [
            Transaction(date=pendulum.datetime(2019, 1, 1),
                        action=Action.BUY,
                        asset=AssetValue(1000, "AAPL"),
                        fiat_value=FiatValue(100, Currency.DOLLAR)),
            Transaction(date=pendulum.datetime(2020, 1, 1),
                        action=Action.BUY,
                        asset=AssetValue(1000, "AAPL"),
                        fiat_value=FiatValue(100, Currency.DOLLAR)),
            Transaction(date=pendulum.datetime(2021, 1, 1),
                        action=Action.SELL,
                        asset=AssetValue(1000, "AAPL"),
                        fiat_value=FiatValue(100, Currency.DOLLAR)),
            Transaction(date=pendulum.datetime(2022, 1, 1),
                        action=Action.SELL,
                        asset=AssetValue(1000, "AAPL"),
                        fiat_value=FiatValue(100, Currency.DOLLAR)),
        ]
        self.assertListEqual(new_transactions, expected_transactions)