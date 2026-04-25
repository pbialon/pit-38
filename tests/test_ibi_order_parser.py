from pathlib import Path
from unittest import TestCase

import pendulum

from pit38.plugins.stock.ibi_capital.order_parser import (
    OrderParseError,
    parse_order_report,
)

FIXTURES = Path(__file__).parent / "e2e" / "fixtures"


class TestParseOrderReport(TestCase):
    def test_parses_rsu_fixture(self):
        text = (FIXTURES / "ibi_order_fake_rsu.txt").read_text()

        parsed = parse_order_report(text)

        self.assertEqual(parsed.order_number, "9000001")
        self.assertEqual(parsed.company, "acme.com")
        self.assertEqual(parsed.plan, "Acme 2022 RSU")
        self.assertEqual(parsed.grant_date, pendulum.datetime(2023, 1, 10))
        self.assertEqual(parsed.execution_date, pendulum.datetime(2025, 2, 20))
        self.assertEqual(parsed.shares, 20)
        self.assertEqual(parsed.sale_price, 100.0)
        self.assertEqual(parsed.total_amount, 2000.0)
        self.assertEqual(parsed.total_fees, 6.0)
        self.assertEqual(parsed.price_for_tax, 0.0)

    def test_parses_espp_fixture(self):
        text = (FIXTURES / "ibi_order_fake_espp.txt").read_text()

        parsed = parse_order_report(text)

        self.assertEqual(parsed.order_number, "9000002")
        self.assertEqual(parsed.plan, "Acme ESPP")
        self.assertEqual(parsed.shares, 10)
        self.assertEqual(parsed.total_amount, 1200.0)
        self.assertEqual(parsed.total_fees, 5.2)
        # ESPP encodes cost-basis-per-share in Price For Tax, unlike RSU.
        self.assertEqual(parsed.price_for_tax, 50.0)

    def test_parses_thousands_separator_in_amount(self):
        text = (FIXTURES / "ibi_order_fake_rsu.txt").read_text()
        # Swap in a larger amount to exercise the 1,234.56 formatting that
        # real IBI exports use (e.g. USD 13,731.52).
        text = text.replace(
            "Total Amount Due to Order 20 USD 100.0000 USD 2,000.00",
            "Total Amount Due to Order 47 USD 309.2001 USD 14,532.40",
        )

        parsed = parse_order_report(text)

        self.assertEqual(parsed.shares, 47)
        self.assertEqual(parsed.sale_price, 309.2001)
        self.assertEqual(parsed.total_amount, 14532.40)

    def test_raises_on_missing_execution_date(self):
        text = (FIXTURES / "ibi_order_fake_rsu.txt").read_text()
        stripped = text.replace("Execution Date: February 20, 2025", "")

        with self.assertRaises(OrderParseError) as ctx:
            parse_order_report(stripped)
        self.assertIn("Execution Date", str(ctx.exception))

    def test_raises_on_missing_total_fees(self):
        text = (FIXTURES / "ibi_order_fake_rsu.txt").read_text()
        stripped = text.replace(
            "Total Fees (THE ABOVE FEES DO NOT INCLUDE TRANSFER FEES) USD 6.00",
            "",
        )

        with self.assertRaises(OrderParseError) as ctx:
            parse_order_report(stripped)
        self.assertIn("Total Fees", str(ctx.exception))

    def test_total_fees_line_without_paren_note(self):
        # Defensive: if IBI ever drops the parenthetical note, the parser
        # still extracts the total fee value.
        text = (FIXTURES / "ibi_order_fake_rsu.txt").read_text()
        text = text.replace(
            "Total Fees (THE ABOVE FEES DO NOT INCLUDE TRANSFER FEES) USD 6.00",
            "Total Fees USD 6.00",
        )

        parsed = parse_order_report(text)

        self.assertEqual(parsed.total_fees, 6.0)
