from unittest import TestCase

import pendulum
import pathlib

from data_sources.revolut.csv_reader import TransactionsCsvReader
from domain.currency_exchange_service.currencies import FiatValue, Currency
from data_sources.revolut.crypto import CryptoCsvParser
from domain.transactions import Transaction, AssetValue, Action




class TestTsvReader(TestCase):
    def test_read(self):
        filepath = pathlib.Path(__file__).parent.absolute() / "resources" / "example_export.csv"

        reader = TransactionsCsvReader(filepath, CryptoCsvParser)
        transactions = list(reader.read())
        expected = [
            Transaction(
                asset=AssetValue(0.03962455, 'BTC'),
                fiat_value=FiatValue(5000.0, Currency.ZLOTY),
                action=Action.BUY,
                date=pendulum.parse('2021-01-11 13:24:26')
            ),
            Transaction(
                asset=AssetValue(0.03785017, 'BTC'),
                fiat_value=FiatValue(5000.0, Currency.ZLOTY),
                action=Action.BUY,
                date=pendulum.parse('2021-01-11 23:08:00')
            ),
            Transaction(
                asset=AssetValue(0.01, 'BTC'),
                fiat_value=FiatValue(1304.96, Currency.ZLOTY),
                action=Action.SELL,
                date=pendulum.parse('2021-01-29 09:03:37')
            ),
        ]
        self.assertListEqual(transactions, expected)
