from unittest import TestCase

import pendulum
import pathlib

from data_sources.revolut.csv_reader import TransactionsCsvReader
from data_sources.revolut.crypto import CryptoCsvParser
from domain.transactions import Transaction, Action
from tests.utils import btc, zl


class TestCsvReader(TestCase):
    def test_read(self):
        filepath = pathlib.Path(__file__).parent.absolute() / "resources" / "example_export.csv"

        reader = TransactionsCsvReader(filepath, CryptoCsvParser)
        transactions = list(reader.read())
        expected = [
            Transaction(
                asset=btc(0.03962455),
                fiat_value=zl(5000.0),
                action=Action.BUY,
                date=pendulum.parse('2021-01-11 13:24:26')
            ),
            Transaction(
                asset=btc(0.03785017),
                fiat_value=zl(5000.0),
                action=Action.BUY,
                date=pendulum.parse('2021-01-11 23:08:00')
            ),
            Transaction(
                asset=btc(0.01),
                fiat_value=zl(1304.96),
                action=Action.SELL,
                date=pendulum.parse('2021-01-29 09:03:37')
            ),
        ]
        self.assertListEqual(transactions, expected)
