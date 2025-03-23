from unittest import TestCase
from unittest.mock import Mock

import pendulum

from domain.transactions import Transaction, AssetValue, Action
from domain.currency_exchange_service.currencies import FiatValue, Currency
from data_sources.crypto_loader.multi_sources_loader import MultiSourcesLoader


class TestMultiSourcesLoader(TestCase):
    def setUp(self):
        self.mock_loader = Mock()
        self.multi_sources_loader = MultiSourcesLoader(self.mock_loader)

        # Create sample transactions that will be returned by mock
        self.btc_transactions = [
            Transaction(
                asset=AssetValue(0.02, "BTC"),
                fiat_value=FiatValue(8000.00, Currency.ZLOTY),
                action=Action.BUY,
                date=pendulum.parse("2025-01-10 12:34:10")
            ),
            Transaction(
                asset=AssetValue(0.0024, "BTC"),
                fiat_value=FiatValue(960.00, Currency.ZLOTY),
                action=Action.SELL,
                date=pendulum.parse("2025-01-11 09:01:22")
            )
        ]

        self.eth_transactions = [
            Transaction(
                asset=AssetValue(0.05, "ETH"),
                fiat_value=FiatValue(1000.00, Currency.ZLOTY),
                action=Action.BUY,
                date=pendulum.parse("2025-01-09 15:00:00")
            ),
            Transaction(
                asset=AssetValue(0.03, "ETH"),
                fiat_value=FiatValue(800.00, Currency.ZLOTY),
                action=Action.SELL,
                date=pendulum.parse("2025-01-12 18:30:00")
            )
        ]

    def test_load_multiple_files(self):
        # Configure mock to return different transactions for different files
        self.mock_loader.load.side_effect = [
            self.btc_transactions,
            self.eth_transactions
        ]
        
        transactions = self.multi_sources_loader.load(["btc.csv", "eth.csv"])
        
        self.assertEqual(len(transactions), 4)
        
        # Check if transactions are sorted by date
        dates = [t.date for t in transactions]
        self.assertEqual(
            dates,
            [
                pendulum.parse("2025-01-09 15:00:00"),
                pendulum.parse("2025-01-10 12:34:10"),
                pendulum.parse("2025-01-11 09:01:22"),
                pendulum.parse("2025-01-12 18:30:00")
            ]
        )

        # Verify that mock was called correctly
        self.mock_loader.load.assert_any_call("btc.csv")
        self.mock_loader.load.assert_any_call("eth.csv")
        self.assertEqual(self.mock_loader.load.call_count, 2)

    def test_load_with_one_invalid_file(self):
        # Configure mock to raise exception for second file
        self.mock_loader.load.side_effect = [
            self.btc_transactions,
            FileNotFoundError("File not found")
        ]
        
        transactions = self.multi_sources_loader.load(["btc.csv", "nonexistent.csv"])
        
        # Should load transactions from valid file only
        self.assertEqual(len(transactions), 2)
        self.assertEqual(self.mock_loader.load.call_count, 2)

    def test_load_empty_file_list(self):
        transactions = self.multi_sources_loader.load([])
        
        self.assertEqual(len(transactions), 0)
        self.mock_loader.load.assert_not_called() 