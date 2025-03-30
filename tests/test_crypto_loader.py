import os
import tempfile
from unittest import TestCase

import pendulum

from domain.transactions import Action
from domain.currency_exchange_service.currencies import Currency
from data_sources.crypto_loader.csv_loader import Loader


class TestCsvLoader(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.valid_csv_content = """date,operation,amount,symbol,fiat_value,currency
2025-01-10 12:34:10,BUY,0.02000000,BTC,8000.00,PLN
2025-01-11 09:01:22,SELL,0.00240000,BTC,240.00,USD"""
        
        self.invalid_csv_content = """date,operation,amount,symbol,fiat_value,currency
2025-01-10 12:34:10,INVALID,0.02000000,BTC,8000.00,PLN
2025-01-11 09:01:22,SELL,not_a_number,BTC,960.00,PLN"""

    def tearDown(self):
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def _create_temp_file(self, content: str) -> str:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=self.temp_dir) as f:
            f.write(content)
            return f.name

    def test_load_valid_transactions(self):
        file_path = self._create_temp_file(self.valid_csv_content)
        transactions = Loader.load(file_path)

        self.assertEqual(len(transactions), 2)
        
        # Test first transaction
        first_transaction = transactions[0]
        self.assertEqual(first_transaction.action, Action.BUY)
        self.assertEqual(first_transaction.asset.amount, 0.02)
        self.assertEqual(first_transaction.asset.asset_name, "BTC")
        self.assertEqual(first_transaction.fiat_value.amount, 8000.00)
        self.assertEqual(first_transaction.fiat_value.currency, Currency.ZLOTY)
        self.assertEqual(
            first_transaction.date,
            pendulum.parse("2025-01-10 12:34:10")
        )

        # Test second transaction
        second_transaction = transactions[1]
        self.assertEqual(second_transaction.action, Action.SELL)
        self.assertEqual(second_transaction.asset.amount, 0.0024)
        self.assertEqual(second_transaction.asset.asset_name, "BTC")
        self.assertEqual(second_transaction.fiat_value.amount, 240.00)
        self.assertEqual(second_transaction.fiat_value.currency, Currency.DOLLAR)
        self.assertEqual(
            second_transaction.date,
            pendulum.parse("2025-01-11 09:01:22")
        )

    def test_load_invalid_transactions(self):
        file_path = self._create_temp_file(self.invalid_csv_content)
        transactions = Loader.load(file_path)
        
        self.assertEqual(len(transactions), 0)

    def test_load_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            Loader.load("nonexistent_file.csv")

    def test_load_empty_file(self):
        file_path = self._create_temp_file("date,operation,amount,symbol,fiat_value,currency")
        transactions = Loader.load(file_path)
        
        self.assertEqual(len(transactions), 0)

    def test_load_missing_required_column(self):
        invalid_content = """date,operation,symbol,fiat_value,currency
2025-01-10 12:34:10,BUY,BTC,8000.00,PLN"""
        
        file_path = self._create_temp_file(invalid_content)
        transactions = Loader.load(file_path)
        
        self.assertEqual(len(transactions), 0) 