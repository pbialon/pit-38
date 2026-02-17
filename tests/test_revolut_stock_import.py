from unittest import TestCase

import pathlib

from plugins.stock.revolut.csv import CsvService as RevolutStockCsvReader
from plugins.stock.revolut.transaction_row_parser import TransactionRowParser
from tests.utils import buy, sell, google, amazon, meta, usd


class TestCsvReader(TestCase):
    def test_read(self):
        filepath = pathlib.Path(__file__).parent.absolute() / "resources" / "example_stock_export.csv"

        reader = RevolutStockCsvReader(filepath, TransactionRowParser)
        transactions = list(reader.read())

        expected = [
            buy(google(0.28028162), usd(500.0), "2021-01-11T14:33:03.080302Z"),
            buy(amazon(0.07945639), usd(250.0), "2021-01-11T14:35:28.061628Z"),
            buy(meta(0.96264921), usd(250.0), "2021-01-11T14:35:45.617853Z"),
            sell(google(0.28028162), usd(529.68), "2021-01-21T14:30:23.319726Z"),
        ]

        self.assertListEqual(transactions, expected)
