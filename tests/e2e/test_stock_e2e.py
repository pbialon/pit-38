"""End-to-end tests for the stock tax pipeline.

Tests the full flow: broker CSV → plugin import → standardized CSV → loader →
profit calculator → tax calculator → final result.
"""
import pathlib
import tempfile
from unittest import TestCase

from pit38.data_sources.stock_loader.csv_loader import Loader as StockLoader
from pit38.domain.stock.profit.per_stock_calculator import PerStockProfitCalculator
from pit38.domain.stock.profit.profit_calculator import ProfitCalculator
from pit38.domain.tax_service.stock_tax_calculator import StockTaxCalculator
from pit38.plugins.stock.revolut.csv import CsvService
from pit38.plugins.stock.revolut.transaction_row_parser import TransactionRowParser
from pit38.plugins.stock.generic_saver import GenericCsvSaver
from tests.utils import StubExchanger

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


class TestStockFullPipeline(TestCase):
    """Tests the complete stock pipeline with StubExchanger (4.0 USD→PLN)."""

    def test_revolut_import_then_calculate(self):
        revolut_csv = FIXTURES / "revolut_stock_export.csv"

        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as tmp:
            tmp_path = tmp.name

        transactions = list(CsvService(revolut_csv, TransactionRowParser).read())
        GenericCsvSaver.save(transactions, [], tmp_path)

        loaded = StockLoader.load(tmp_path)
        self.assertEqual(len(loaded), len(transactions))

    def test_revolut_real_export_with_bom_and_unknown_operations(self):
        """Regression for #33 — real Revolut CSV has UTF-8 BOM, lowercase
        headers (`date` not `Date`), and non-tax operations (CASH WITHDRAWAL,
        DEPOSIT, TRANSFER). Each broke the parser before; now:
          - BOM is stripped by utf-8-sig encoding
          - Headers normalized to lowercase at read time
          - Unknown operation types are counted and skipped, not crashed
        """
        from pit38.plugins.stock.revolut.operation_row_parser import OperationRowParser

        revolut_csv = FIXTURES / "revolut_stock_real.csv"
        # Sanity: fixture actually has BOM
        self.assertEqual(revolut_csv.read_bytes()[:3], b"\xef\xbb\xbf")

        # Transactions: BUY + SELL rows parsed
        tx_result = CsvService(str(revolut_csv), TransactionRowParser).read_with_summary()
        self.assertEqual(len(tx_result.records), 2, "Should find BUY and SELL")

        # Operations: DIVIDEND row parsed
        op_result = CsvService(str(revolut_csv), OperationRowParser).read_with_summary()
        self.assertEqual(len(op_result.records), 1, "Should find DIVIDEND")

        # Skipped summary includes all non-tax rows
        self.assertEqual(tx_result.skipped_by_type["CASH WITHDRAWAL"], 1)
        self.assertEqual(tx_result.skipped_by_type["DEPOSIT"], 1)
        self.assertEqual(tx_result.skipped_by_type["TRANSFER"], 1)
        self.assertEqual(tx_result.total_skipped, 3)

    def test_standardized_csv_to_tax_result(self):
        csv_path = FIXTURES / "standardized_stock.csv"

        records = StockLoader.load(str(csv_path))
        transactions = [r for r in records if hasattr(r, 'action')]

        exchanger = StubExchanger()
        per_stock = PerStockProfitCalculator(exchanger)
        calculator = ProfitCalculator(exchanger, per_stock)

        profit_txns, _ = calculator.calculate_cumulative_cost_and_income(
            transactions, [], [], [])

        tax_calc = StockTaxCalculator()

        # 2023: sold 5 AAPL for $850
        # cost = 5/10 * $1500 = $750 → 750*4=3000 PLN
        # income = $850 → 850*4=3400 PLN
        result_2023 = tax_calc.calculate_tax_per_year(profit_txns, 2023)
        self.assertGreater(result_2023.income.amount, 0)
        self.assertGreater(result_2023.cost.amount, 0)

        # 2024: sold 5 AAPL ($900) + 5 GOOGL ($700)
        result_2024 = tax_calc.calculate_tax_per_year(profit_txns, 2024)
        self.assertGreater(result_2024.income.amount, 0)
        self.assertGreater(result_2024.cost.amount, 0)
        self.assertEqual(result_2024.tax, result_2024.base_for_tax * 0.19)

    def test_loss_year_followed_by_profit_year(self):
        csv_path = FIXTURES / "standardized_stock_loss.csv"

        records = StockLoader.load(str(csv_path))
        transactions = [r for r in records if hasattr(r, 'action')]

        exchanger = StubExchanger()
        per_stock = PerStockProfitCalculator(exchanger)
        calculator = ProfitCalculator(exchanger, per_stock)

        profit_txns, _ = calculator.calculate_cumulative_cost_and_income(
            transactions, [], [], [])

        tax_calc = StockTaxCalculator()

        result_2023 = tax_calc.calculate_tax_per_year(profit_txns, 2023)
        self.assertLess(result_2023.base_for_tax.amount, 0)
        self.assertEqual(result_2023.tax.amount, 0)

        result_2024 = tax_calc.calculate_tax_per_year(profit_txns, 2024)
        self.assertGreater(result_2024.deductible_loss.amount, 0)
        self.assertGreater(result_2024.base_for_tax.amount, 0)
