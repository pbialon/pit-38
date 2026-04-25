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


class TestImportIbiCapitalCLI(TestCase):
    """CLI integration for ``pit38 import ibi-capital``.

    pdfplumber's PDF-extraction path is covered directly in
    test_ibi_pdf_reader.py. Here we mock it out so tests stay text-
    fixture-based (no binary fixtures, no PII risk) while still driving
    the full CLI function end-to-end.
    """

    RSU_TEXT = (FIXTURES / "ibi_order_fake_rsu.txt").read_text()

    def _invoke(self, args, extract_text_return):
        """Invoke the CLI with extract_text mocked to a canned string."""
        with patch(
            "pit38.plugins.stock.ibi_capital.pdf_reader.extract_text",
            return_value=extract_text_return,
        ):
            return CliRunner().invoke(main, args)

    def test_import_single_pdf_with_ticker_override(self):
        with CliRunner().isolated_filesystem():
            # The file's content doesn't matter — extract_text is mocked.
            # click.Path(exists=True) just needs the file to be present.
            pathlib.Path("order.pdf").write_bytes(b"%PDF-1.4\n%%EOF\n")

            result = self._invoke(
                [
                    "import", "ibi-capital",
                    "-i", "order.pdf",
                    "-o", "out.csv",
                    "--ticker", "ACME",
                    "-ll", "ERROR",
                ],
                extract_text_return=self.RSU_TEXT,
            )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("Saved", result.output)
            self.assertIn("IBI Capital PDF", result.output)
            csv_text = pathlib.Path("out.csv").read_text()
            self.assertIn("BUY", csv_text)
            self.assertIn("SELL", csv_text)
            self.assertIn("ACME", csv_text)

    def test_directory_input_scans_pdfs(self):
        with CliRunner().isolated_filesystem():
            pathlib.Path("orders").mkdir()
            pathlib.Path("orders/a.pdf").write_bytes(b"%PDF-1.4\n%%EOF\n")
            pathlib.Path("orders/b.pdf").write_bytes(b"%PDF-1.4\n%%EOF\n")
            # Non-PDF files in the same directory are ignored.
            pathlib.Path("orders/readme.txt").write_text("not a pdf")

            # Both PDFs resolve through the same mocked text — this is
            # fine for asserting "everything got processed", just not for
            # per-file content validation.
            result = self._invoke(
                [
                    "import", "ibi-capital",
                    "-i", "orders",
                    "-o", "out.csv",
                    "--ticker", "ACME",
                    "-ll", "ERROR",
                ],
                extract_text_return=self.RSU_TEXT,
            )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("2 IBI Capital PDF", result.output)

    def test_no_pdfs_found_aborts_cleanly(self):
        with CliRunner().isolated_filesystem():
            pathlib.Path("orders").mkdir()
            # Empty directory — click.Path(exists=True) accepts the dir,
            # but the rglob finds zero PDFs.

            result = self._invoke(
                [
                    "import", "ibi-capital",
                    "-i", "orders",
                    "-o", "out.csv",
                    "-ll", "ERROR",
                ],
                extract_text_return="",
            )

            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("No PDF files", result.output)

    def test_unknown_company_without_ticker_errors(self):
        with CliRunner().isolated_filesystem():
            pathlib.Path("order.pdf").write_bytes(b"%PDF-1.4\n%%EOF\n")

            # RSU fixture has Company: acme.com which is NOT in
            # companies.json — without --ticker, the resolver must fail
            # with a helpful message rather than silently defaulting.
            result = self._invoke(
                [
                    "import", "ibi-capital",
                    "-i", "order.pdf",
                    "-o", "out.csv",
                    "-ll", "ERROR",
                ],
                extract_text_return=self.RSU_TEXT,
            )

            self.assertNotEqual(result.exit_code, 0)
            # Click wraps uncaught exceptions; the inner message surfaces
            # in `result.exception` or `result.output` depending on mode.
            error_text = str(result.exception) if result.exception else result.output
            self.assertIn("acme.com", error_text)
            self.assertIn("--ticker", error_text)
