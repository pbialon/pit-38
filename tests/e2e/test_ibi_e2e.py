"""End-to-end test for the IBI Capital plugin.

Exercises: text fixture → order_parser → record_builder → GenericCsvSaver
→ StockLoader round-trip. We bypass ``pdf_reader.extract_text`` because
pdfplumber PDF output is deterministic for a given template and testing
it adds no extra assurance; what matters is that the parser → builder →
saver → loader chain holds.
"""
import pathlib
import tempfile
from unittest import TestCase

from pit38.data_sources.stock_loader.csv_loader import Loader as StockLoader
from pit38.domain.transactions import Action, Transaction
from pit38.plugins.stock.generic_saver import GenericCsvSaver
from pit38.plugins.stock.ibi_capital.order_parser import parse_order_report
from pit38.plugins.stock.ibi_capital.record_builder import build_records

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


class TestIbiPipeline(TestCase):
    def test_rsu_and_espp_fixtures_roundtrip_through_loader(self):
        rsu_text = (FIXTURES / "ibi_order_fake_rsu.txt").read_text()
        espp_text = (FIXTURES / "ibi_order_fake_espp.txt").read_text()

        transactions = []
        fees = []
        for text in (rsu_text, espp_text):
            parsed = parse_order_report(text)
            t, f = build_records(parsed, ticker="ACME")
            transactions.extend(t)
            fees.extend(f)

        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as tmp:
            tmp_path = tmp.name
        GenericCsvSaver.save(transactions, fees, tmp_path)

        loaded = StockLoader.load(tmp_path)

        # Loader returns a mixed list of Transaction + ServiceFee. Filter
        # to transactions for the FIFO assertions.
        txs = [item for item in loaded if isinstance(item, Transaction)]

        buy_sell = [t for t in txs if t.action in (Action.BUY, Action.SELL)]
        self.assertEqual(len(buy_sell), 4)

        # RSU: BUY fiat_value is 0 (zero cost basis).
        rsu_buys = [
            t for t in txs
            if t.action == Action.BUY and t.fiat_value.amount == 0
        ]
        self.assertEqual(len(rsu_buys), 1)

        # ESPP: BUY fiat_value = 10 shares × $50 Price For Tax = $500.
        espp_buys = [
            t for t in txs
            if t.action == Action.BUY and t.fiat_value.amount == 500.0
        ]
        self.assertEqual(len(espp_buys), 1)

        # SELL proceeds match Total Amount Due to Order from fixtures.
        sell_amounts = sorted(
            t.fiat_value.amount for t in txs if t.action == Action.SELL
        )
        self.assertEqual(sell_amounts, [1200.0, 2000.0])
