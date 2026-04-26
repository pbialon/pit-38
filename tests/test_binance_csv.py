"""Unit tests for the Binance Spot export parser.

Covers the post-2025 format where the time column was renamed
``UTC_Time`` → ``Time`` and the year in timestamps shortened (2024 → 24).
"""
import pathlib
from unittest import TestCase

import pendulum

from pit38.domain.transactions import Action, AssetValue
from pit38.plugins.crypto.binance.csv import BinanceTransactionProcessor

FIXTURE = pathlib.Path(__file__).parent / "e2e" / "fixtures" / "binance_transaction_history.csv"


class TestBinanceCsvReader(TestCase):
    def test_reads_fixture_without_crashing(self):
        transactions = BinanceTransactionProcessor().read(str(FIXTURE))
        self.assertEqual(len(transactions), 2)

    def test_deposit_rows_are_skipped(self):
        # Deposit rows top up the Spot wallet with fiat but carry no
        # buy/sell intent — they must not leak into the output. Our
        # fixture has 1 Deposit; parsed output should never contain
        # a PLN-denominated asset leg.
        transactions = BinanceTransactionProcessor().read(str(FIXTURE))

        self.assertTrue(all(tx.asset.asset_name in {"BTC", "ETH"} for tx in transactions))

    def test_convert_pair_becomes_single_buy(self):
        transactions = BinanceTransactionProcessor().read(str(FIXTURE))
        converts = [t for t in transactions if t.date == pendulum.datetime(2024, 1, 15, 12, 0, 0)]

        self.assertEqual(len(converts), 1)
        self.assertEqual(converts[0].action, Action.BUY)
        self.assertEqual(converts[0].asset, AssetValue(0.002, "BTC"))
        # The current Binance parser stores the raw coin string ("PLN")
        # on FiatValue.currency rather than Currency.ZLOTY — pre-existing
        # quirk that's outside the scope of this format-change fix. We
        # assert on components so the test stays honest about observed
        # behavior without silently endorsing the string-vs-enum drift.
        self.assertEqual(converts[0].fiat_value.amount, 500.0)
        self.assertEqual(str(converts[0].fiat_value.currency), "PLN")

    def test_transaction_triple_aggregates_fee_into_asset(self):
        # Transaction Buy/Fee/Spend triples: the asset received is
        # buy_amount + |fee_amount| (the fee is a crypto-denominated
        # deduction from the buy, so the cost basis in PLN covers both).
        transactions = BinanceTransactionProcessor().read(str(FIXTURE))
        triples = [t for t in transactions if t.date == pendulum.datetime(2024, 1, 20, 14, 30, 0)]

        self.assertEqual(len(triples), 1)
        tx = triples[0]
        self.assertEqual(tx.action, Action.BUY)
        # 0.001 buy + 0.000001 fee = 0.001001 BTC
        self.assertAlmostEqual(tx.asset.amount, 0.001001, places=6)
        self.assertEqual(tx.asset.asset_name, "BTC")
        self.assertEqual(tx.fiat_value.amount, 200.0)
        self.assertEqual(str(tx.fiat_value.currency), "PLN")

    def test_output_sorted_by_date(self):
        transactions = BinanceTransactionProcessor().read(str(FIXTURE))
        dates = [t.date for t in transactions]
        self.assertEqual(dates, sorted(dates))

    def test_yy_year_parsing(self):
        # Guard against accidental revert to "%Y-%m-%d" — that would
        # parse "24-01-15" as year 24 AD and silently produce garbage
        # dates, which FIFO would then match wrongly.
        transactions = BinanceTransactionProcessor().read(str(FIXTURE))
        for tx in transactions:
            self.assertGreaterEqual(tx.date.year, 2000)
