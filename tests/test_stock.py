from unittest import TestCase

import pathlib

from data_sources.revolut.csv_reader import TransactionsCsvReader
from data_sources.revolut.stock.transaction_csv_parser import TransactionStockCsvParser
from tests.utils import buy, sell, google, amazon, meta, usd


class TestCsvReader(TestCase):
    def test_read(self):
        filepath = pathlib.Path(__file__).parent.absolute() / "resources" / "example_stock_export.csv"

        reader = TransactionsCsvReader(filepath, TransactionStockCsvParser)
        transactions = list(reader.read())

        expected = [
            buy(google(0.28028162), usd(500.0), "2021-01-11 14:33:03"),
            buy(amazon(0.07945639), usd(250.0), "2021-01-11 14:35:28"),
            buy(meta(0.96264921), usd(250.0), "2021-01-11 14:35:45"),
            sell(google(0.28028162), usd(529.68), "2021-01-21 14:30:23"),
        ]

        self.assertListEqual(transactions, expected)
