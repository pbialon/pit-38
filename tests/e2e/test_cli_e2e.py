"""End-to-end tests for CLI commands.

Tests that CLI entry points run without crashing on valid input.
Uses Click's test runner to avoid subprocess overhead.
"""
import pathlib
from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from pit38.stock import stocks
from pit38.crypto import crypto
from pit38.cli import main

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


class FakeExchangeRatesProvider:
    def get_rate(self, currency, date):
        return 4.0


class TestStockCLI(TestCase):

    @patch("pit38.exchanger.create_exchanger")
    def test_stock_command_runs(self, mock_exchanger):
        from pit38.domain.currency_exchange_service.exchanger import Exchanger
        from pit38.domain.calendar_service.calendar import Calendar
        mock_exchanger.return_value = Exchanger(FakeExchangeRatesProvider(), Calendar())

        runner = CliRunner()
        csv_path = str(FIXTURES / "standardized_stock.csv")
        result = runner.invoke(stocks, ["-f", csv_path, "-y", "2024", "-ll", "ERROR"])

        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn("Stock Tax Summary", result.output)


class TestCryptoCLI(TestCase):

    @patch("pit38.exchanger.create_exchanger")
    def test_crypto_command_runs(self, mock_exchanger):
        from pit38.domain.currency_exchange_service.exchanger import Exchanger
        from pit38.domain.calendar_service.calendar import Calendar
        mock_exchanger.return_value = Exchanger(FakeExchangeRatesProvider(), Calendar())

        runner = CliRunner()
        csv_path = str(FIXTURES / "standardized_crypto.csv")
        result = runner.invoke(crypto, ["-f", csv_path, "-y", "2024", "-ll", "ERROR"])

        self.assertEqual(result.exit_code, 0, msg=result.output)


class TestImportCLI(TestCase):

    def test_import_revolut_stock(self):
        runner = CliRunner()
        csv_path = str(FIXTURES / "revolut_stock_export.csv")

        with runner.isolated_filesystem():
            result = runner.invoke(main, [
                "import", "revolut-stock",
                "-i", csv_path,
                "-o", "output.csv",
                "-ll", "ERROR",
            ])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("Saved", result.output)
            self.assertTrue(pathlib.Path("output.csv").exists())
