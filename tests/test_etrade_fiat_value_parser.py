from unittest import TestCase
from pit38.domain.currency_exchange_service.currencies import Currency, FiatValue
from pit38.plugins.stock.etrade.row_parser import FiatValueParser


class TestFiatValueParser(TestCase):
    def test_parse_dollar(self):
        raw_fiat_value = "$100,50"
        expected_fiat_value = FiatValue(amount=100.50, currency=Currency.DOLLAR)

        parsed_fiat_value = FiatValueParser.parse(raw_fiat_value)

        self.assertEqual(parsed_fiat_value, expected_fiat_value)

    def test_parse_dollar_big_number(self):
        raw_fiat_value = "$25 001,75"
        expected_fiat_value = FiatValue(amount=25001.75, currency=Currency.DOLLAR)

        parsed_fiat_value = FiatValueParser.parse(raw_fiat_value)

        self.assertEqual(parsed_fiat_value, expected_fiat_value)

    # ─── Tests added with the shared-normalization migration ──

    def test_parse_euro(self):
        """Euro symbol variant (same code path as dollar after migration)."""
        self.assertEqual(
            FiatValueParser.parse("€250,00"),
            FiatValue(amount=250.00, currency=Currency.EURO),
        )

    def test_parse_negative_symbol_amount(self):
        """Negative with minus between symbol and amount: '$-0,15'."""
        self.assertEqual(
            FiatValueParser.parse("$-0,15"),
            FiatValue(amount=0.15, currency=Currency.DOLLAR),
        )

    def test_parse_nbsp_thousand_separator(self):
        """Some E*Trade exports use non-breaking space (U+00A0) as the
        thousand separator instead of regular space. parse_amount strips
        both uniformly."""
        self.assertEqual(
            FiatValueParser.parse("$25\xa0001,75"),
            FiatValue(amount=25001.75, currency=Currency.DOLLAR),
        )

    def test_parse_unknown_symbol_raises(self):
        """Currency symbol outside SYMBOL_TO_CURRENCY raises cleanly
        (not a silent None that blows up downstream)."""
        with self.assertRaises(ValueError) as ctx:
            FiatValueParser.parse("£100,00")
        self.assertIn("Unknown currency symbol", str(ctx.exception))
