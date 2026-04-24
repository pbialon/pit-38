"""Tests for pit38.plugins.stock.revolut.csv.CsvService.

Focuses on the `read_with_summary()` flow introduced for #33: liberal
parsing that counts skipped-by-type instead of failing silently.

These are mid-level tests — they exercise the full CsvService + row
parser integration, but read from temp files rather than hitting the
real broker fixtures. That lets us dial in specific edge cases.
"""
import os
import tempfile
from unittest import TestCase

from pit38.plugins.stock.revolut.csv import CsvService, ReadResult
from pit38.plugins.stock.revolut.transaction_row_parser import TransactionRowParser
from pit38.plugins.stock.revolut.operation_row_parser import OperationRowParser


HEADER = "date,Ticker,Type,Quantity,Price per share,Total Amount,Currency,FX Rate\n"


class TestReadResultDataclass(TestCase):
    def test_total_skipped_empty_counter(self):
        result = ReadResult(records=[])
        self.assertEqual(result.total_skipped, 0)

    def test_total_skipped_sums_all_types(self):
        from collections import Counter
        result = ReadResult(
            records=[],
            skipped_by_type=Counter({"CASH WITHDRAWAL": 3, "DEPOSIT": 2})
        )
        self.assertEqual(result.total_skipped, 5)


class TestCsvServiceReadWithSummary(TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        )
        self.tmp.close()
        self.path = self.tmp.name

    def tearDown(self):
        os.unlink(self.path)

    def _write(self, body: str) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(HEADER + body)

    # ─── Transaction parser: only BUY/SELL produce records ──

    def test_all_known_tax_operations_produce_records(self):
        """BUY + SELL rows yield transactions, empty skip counter."""
        self._write(
            "2024-01-01T10:00:00Z,AAPL,BUY - MARKET,10,USD 150.00,USD 1500.00,USD,0.25\n"
            "2024-02-01T11:00:00Z,AAPL,SELL - MARKET,5,USD 180.00,USD 900.00,USD,0.26\n"
        )

        result = CsvService(self.path, TransactionRowParser).read_with_summary()

        self.assertEqual(len(result.records), 2)
        self.assertEqual(result.total_skipped, 0)
        self.assertEqual(dict(result.skipped_by_type), {})

    def test_unknown_operations_counted_separately_by_type(self):
        """Different unknown operation types are tallied by type — user
        sees CASH WITHDRAWAL and DEPOSIT as separate counts."""
        self._write(
            "2024-01-01T10:00:00Z,,CASH WITHDRAWAL,,,USD -100.00,USD,0.25\n"
            "2024-01-02T10:00:00Z,,DEPOSIT,,,USD 500.00,USD,0.25\n"
            "2024-01-03T10:00:00Z,,CASH WITHDRAWAL,,,USD -50.00,USD,0.25\n"
        )

        result = CsvService(self.path, TransactionRowParser).read_with_summary()

        self.assertEqual(len(result.records), 0)
        self.assertEqual(result.total_skipped, 3)
        self.assertEqual(result.skipped_by_type["CASH WITHDRAWAL"], 2)
        self.assertEqual(result.skipped_by_type["DEPOSIT"], 1)

    def test_mixed_known_and_unknown_operations(self):
        """Real-world mix: some taxable, some not. Each lands in the
        right bucket."""
        self._write(
            "2024-01-01T10:00:00Z,AAPL,BUY - MARKET,10,USD 150.00,USD 1500.00,USD,0.25\n"
            "2024-01-02T10:00:00Z,,CASH WITHDRAWAL,,,USD -100.00,USD,0.25\n"
            "2024-01-03T10:00:00Z,AAPL,SELL - MARKET,5,USD 180.00,USD 900.00,USD,0.26\n"
            "2024-01-04T10:00:00Z,,TRANSFER,,,USD -50.00,USD,0.25\n"
        )

        result = CsvService(self.path, TransactionRowParser).read_with_summary()

        self.assertEqual(len(result.records), 2, "BUY and SELL")
        self.assertEqual(result.total_skipped, 2, "CASH WITHDRAWAL and TRANSFER")
        self.assertEqual(result.skipped_by_type["CASH WITHDRAWAL"], 1)
        self.assertEqual(result.skipped_by_type["TRANSFER"], 1)

    def test_empty_operation_column_tagged_explicitly(self):
        """Row with empty Type column gets reported as `<empty>` so the
        user knows the CSV has malformed rows, not just unknown types."""
        self._write(
            "2024-01-01T10:00:00Z,AAPL,,10,USD 150.00,USD 1500.00,USD,0.25\n"
        )

        result = CsvService(self.path, TransactionRowParser).read_with_summary()

        self.assertEqual(len(result.records), 0)
        self.assertEqual(result.total_skipped, 1)
        self.assertIn("<empty>", result.skipped_by_type)

    # ─── Operation parser: only DIVIDEND/SERVICE_FEE/STOCK_SPLIT ──

    def test_operation_parser_handles_dividend_and_skips_transactions(self):
        """OperationRowParser skips BUY/SELL (their parser handles
        them). But BUY/SELL are *known* operations — they go in their
        own `records` list of this parser as None via parse() returning
        None, not as skipped-by-type. Only truly unknown ops count.
        """
        self._write(
            "2024-01-01T10:00:00Z,AAPL,BUY - MARKET,10,USD 150.00,USD 1500.00,USD,0.25\n"
            "2024-02-01T11:00:00Z,MSFT,DIVIDEND,,,USD 2.50,USD,0.25\n"
            "2024-03-01T12:00:00Z,,CASH WITHDRAWAL,,,USD -50.00,USD,0.25\n"
        )

        result = CsvService(self.path, OperationRowParser).read_with_summary()

        # Only 1 record (the dividend). BUY is known, skipped by parse()
        # (returns None), not counted.
        self.assertEqual(len(result.records), 1)
        # CASH WITHDRAWAL is unknown — counted
        self.assertEqual(result.total_skipped, 1)
        self.assertEqual(result.skipped_by_type["CASH WITHDRAWAL"], 1)
        # BUY is a known operation type, not in skipped summary
        self.assertNotIn("BUY - MARKET", result.skipped_by_type)

    # ─── Backward compatibility: read() returns records only ──

    def test_read_returns_records_without_summary(self):
        """Legacy `read()` call site (if any) gets a plain list."""
        self._write(
            "2024-01-01T10:00:00Z,AAPL,BUY - MARKET,10,USD 150.00,USD 1500.00,USD,0.25\n"
        )

        records = CsvService(self.path, TransactionRowParser).read()
        self.assertEqual(len(records), 1)
        # Not a ReadResult — just a list
        self.assertIsInstance(records, list)

    # ─── BOM tolerance at CsvService level ─────────────────

    def test_bom_prefixed_file_reads_correctly(self):
        """End-to-end: CsvService opens a BOM-prefixed file via
        open_csv_reader and parses rows — no KeyError on 'date'."""
        with open(self.path, "wb") as f:
            f.write(b"\xef\xbb\xbf")
            f.write(HEADER.encode("utf-8"))
            f.write(
                b"2024-01-01T10:00:00Z,AAPL,BUY - MARKET,10,USD 150.00,USD 1500.00,USD,0.25\n"
            )

        result = CsvService(self.path, TransactionRowParser).read_with_summary()

        self.assertEqual(len(result.records), 1)
        self.assertEqual(result.total_skipped, 0)
