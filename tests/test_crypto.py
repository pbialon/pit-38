from unittest import TestCase

import pathlib

from data_sources.revolut.csv_reader import TransactionsCsvReader
from data_sources.revolut.crypto import CryptoCsvParser
from tests.utils import btc, usd, zl, buy, sell


class TestCsvReader(TestCase):
    def test_read(self):
        filepath = pathlib.Path(__file__).parent.absolute() / "resources" / "example_crypto_export.csv"

        reader = TransactionsCsvReader(filepath, CryptoCsvParser)
        transactions = list(reader.read())
        expected = [
            buy(btc(0.03962455), zl(5000.0), "2021-01-11 13:24:26"),
            buy(btc(0.03785017), zl(5000.0), "2021-01-11 23:08:00"),
            sell(btc(0.01), zl(1304.96), "2021-01-29 09:03:37"),
            sell(btc(0.01), zl(1353.53), "2021-01-29 09:25:31"),
            buy(btc(0.002084), usd(100.0), "2021-02-12 14:50:13"),
        ]
        self.assertListEqual(transactions, expected)
