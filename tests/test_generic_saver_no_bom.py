"""Regression tests: our output CSVs must NOT contain a UTF-8 BOM.

Postel's law applied to #33: we tolerate BOM on input (some brokers
include it), but we emit clean UTF-8 on output. This keeps our
standardized CSV format minimal and interoperable with anything
downstream that reads plain UTF-8.
"""
import os
import pathlib
import tempfile
from unittest import TestCase

import pendulum

from pit38.domain.currency_exchange_service.currencies import Currency, FiatValue
from pit38.domain.transactions import Action, AssetValue, Transaction
from pit38.plugins.crypto.generic_saver import GenericCsvSaver as CryptoSaver
from pit38.plugins.stock.generic_saver import GenericCsvSaver as StockSaver


BOM = b"\xef\xbb\xbf"


def _sample_transaction():
    return Transaction(
        asset=AssetValue(1.0, "AAPL"),
        fiat_value=FiatValue(150.00, Currency.DOLLAR),
        action=Action.BUY,
        date=pendulum.parse("2024-01-01T10:00:00Z"),
    )


class TestStockSaverNoBOM(TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        )
        self.tmp.close()
        self.path = self.tmp.name

    def tearDown(self):
        os.unlink(self.path)

    def test_output_does_not_start_with_bom(self):
        """Stock saver must emit plain UTF-8, no BOM. If someone changes
        the encoding default, this test fires."""
        StockSaver.save([_sample_transaction()], [], self.path)

        raw = pathlib.Path(self.path).read_bytes()
        self.assertFalse(
            raw.startswith(BOM),
            f"Output CSV starts with BOM ({raw[:3]!r}). "
            f"Writer should use plain utf-8, not utf-8-sig.",
        )

    def test_output_is_valid_utf8(self):
        """Defensive: output is decodable as utf-8 (no stray bytes)."""
        StockSaver.save([_sample_transaction()], [], self.path)

        raw = pathlib.Path(self.path).read_bytes()
        # Will raise UnicodeDecodeError if malformed
        raw.decode("utf-8")

    def test_output_readable_back_by_our_loader(self):
        """Round-trip: write with StockSaver, read with our loader,
        verify no BOM-related breakage."""
        from pit38.data_sources.stock_loader.csv_loader import Loader

        StockSaver.save([_sample_transaction()], [], self.path)

        loaded = Loader.load(self.path)
        self.assertEqual(len(loaded), 1)


class TestCryptoSaverNoBOM(TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        )
        self.tmp.close()
        self.path = self.tmp.name

    def tearDown(self):
        os.unlink(self.path)

    def test_output_does_not_start_with_bom(self):
        """Crypto saver must also emit plain UTF-8, no BOM."""
        CryptoSaver.save([_sample_transaction()], self.path)

        raw = pathlib.Path(self.path).read_bytes()
        self.assertFalse(
            raw.startswith(BOM),
            f"Output CSV starts with BOM ({raw[:3]!r}).",
        )
