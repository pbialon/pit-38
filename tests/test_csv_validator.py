import os
import tempfile
from unittest import TestCase

from data_sources.crypto_loader.csv_validator import CsvValidator


class TestCsvValidator(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.valid_csv_content = """date,operation,amount,symbol,fiat_value,currency
2025-01-10 12:34:10,BUY,0.02000000,BTC,8000.00,PLN
2025-01-11 09:01:22,SELL,0.00240000,BTC,960.00,PLN"""

    def tearDown(self):
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def _create_temp_file(self, content: str) -> str:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=self.temp_dir) as f:
            f.write(content)
            return f.name

    def test_valid_csv(self):
        file_path = self._create_temp_file(self.valid_csv_content)
        errors = CsvValidator.validate(file_path)
        self.assertEqual(len(errors), 0)

    def test_missing_columns(self):
        content = """date,operation,amount,fiat_value,currency
2025-01-10 12:34:10,BUY,0.02000000,8000.00,PLN"""
        
        file_path = self._create_temp_file(content)
        errors = CsvValidator.validate(file_path)
        
        self.assertEqual(len(errors), 1)
        self.assertIn("Missing required columns: symbol", str(errors[0]))

    def test_invalid_date_format(self):
        content = """date,operation,amount,symbol,fiat_value,currency
invalid_date,BUY,0.02000000,BTC,8000.00,PLN"""
        
        file_path = self._create_temp_file(content)
        errors = CsvValidator.validate(file_path)
        
        self.assertEqual(len(errors), 1)
        self.assertIn("Invalid date format", str(errors[0]))

    def test_invalid_operation(self):
        content = """date,operation,amount,symbol,fiat_value,currency
2025-01-10 12:34:10,INVALID,0.02000000,BTC,8000.00,PLN"""
        
        file_path = self._create_temp_file(content)
        errors = CsvValidator.validate(file_path)
        
        self.assertEqual(len(errors), 1)
        self.assertIn("Operation must be one of: BUY, SELL", str(errors[0]))

    def test_invalid_amount(self):
        content = """date,operation,amount,symbol,fiat_value,currency
2025-01-10 12:34:10,BUY,-0.02000000,BTC,8000.00,PLN"""
        
        file_path = self._create_temp_file(content)
        errors = CsvValidator.validate(file_path)
        
        self.assertEqual(len(errors), 1)
        self.assertIn("Amount must be positive", str(errors[0]))

    def test_empty_symbol(self):
        content = """date,operation,amount,symbol,fiat_value,currency
2025-01-10 12:34:10,BUY,0.02000000,,8000.00,PLN"""
        
        file_path = self._create_temp_file(content)
        errors = CsvValidator.validate(file_path)
        
        self.assertEqual(len(errors), 1)
        self.assertIn("Symbol cannot be empty", str(errors[0]))

    def test_invalid_fiat_value(self):
        content = """date,operation,amount,symbol,fiat_value,currency
2025-01-10 12:34:10,BUY,0.02000000,BTC,invalid,PLN"""
        
        file_path = self._create_temp_file(content)
        errors = CsvValidator.validate(file_path)
        
        self.assertEqual(len(errors), 1)
        self.assertIn("could not convert string to float", str(errors[0]))

    def test_invalid_currency(self):
        content = """date,operation,amount,symbol,fiat_value,currency
2025-01-10 12:34:10,BUY,0.02000000,BTC,8000.00,XYZ"""
        
        file_path = self._create_temp_file(content)
        errors = CsvValidator.validate(file_path)
        
        self.assertEqual(len(errors), 1)
        self.assertIn("Row 1: Invalid value 'XYZ' in column 'currency'", str(errors[0]))

    def test_multiple_errors(self):
        content = """date,operation,amount,symbol,fiat_value,currency
invalid_date,INVALID,-0.02000000,,invalid,XYZ"""
        
        file_path = self._create_temp_file(content)
        errors = CsvValidator.validate(file_path)
        
        self.assertEqual(len(errors), 6)  # date, operation, amount, symbol, fiat_value, currency

    def test_nonexistent_file(self):
        errors = CsvValidator.validate("nonexistent_file.csv")
        
        self.assertEqual(len(errors), 1)
        self.assertIn("Failed to read CSV file", str(errors[0])) 