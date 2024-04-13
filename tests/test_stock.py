from unittest import TestCase

import pathlib

from data_sources.csv_reader import TransactionsCsvReader
from data_sources.revolut.stock.transaction_csv_parser import TransactionStockCsvParser
from tests.utils import buy, sell, google, amazon, meta, usd


class TestCsvReader(TestCase):
    def test_read(self):
        filepath = pathlib.Path(__file__).parent.absolute() / "resources" / "example_stock_export.csv"

        reader = TransactionsCsvReader(filepath, TransactionStockCsvParser)
        transactions = list(reader.read())

        expected = [
            buy(google(0.28028162), usd(500.0), "2021-01-11T14:33:03.080302Z"),
            buy(amazon(0.07945639), usd(250.0), "2021-01-11T14:35:28.061628Z"),
            buy(meta(0.96264921), usd(250.0), "2021-01-11T14:35:45.617853Z"),
            sell(google(0.28028162), usd(529.68), "2021-01-21T14:30:23.319726Z"),
        ]

        self.assertListEqual(transactions, expected)
