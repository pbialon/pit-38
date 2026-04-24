"""Unit tests for pit38.plugins.normalization.

The shared module centralizes two kinds of CSV-value normalization used
across broker plugins (Revolut, E*Trade). These tests pin the behaviour
so migrations to a new broker don't accidentally break assumptions.
"""
from unittest import TestCase

from pit38.plugins.normalization import normalize_currency_layout, parse_amount


class TestNormalizeCurrencyLayout(TestCase):
    # ─── Already canonical (no-op cases) ──────────────

    def test_code_with_amount_unchanged(self):
        self.assertEqual(normalize_currency_layout("USD 529.68"), "USD 529.68")

    def test_minus_after_code_already_canonical(self):
        """Primary regression for @inobrevi's #33 comment."""
        self.assertEqual(normalize_currency_layout("USD -0.07"), "USD -0.07")

    # ─── Sign rewrites ────────────────────────────────

    def test_leading_minus_code_moved_past_currency(self):
        self.assertEqual(normalize_currency_layout("-USD 529.68"), "USD -529.68")

    def test_leading_minus_symbol_moved_and_spaced(self):
        self.assertEqual(normalize_currency_layout("-$529.68"), "$ -529.68")

    def test_minus_between_symbol_and_amount_spaced(self):
        self.assertEqual(normalize_currency_layout("$-0.07"), "$ -0.07")

    # ─── Space insertion ──────────────────────────────

    def test_symbol_with_amount_gets_space(self):
        self.assertEqual(normalize_currency_layout("$500"), "$ 500")

    def test_euro_symbol_spaced(self):
        self.assertEqual(normalize_currency_layout("€250.00"), "€ 250.00")

    def test_preserves_internal_whitespace_for_european_format(self):
        """E*Trade's '$25 001,75' must keep the internal space
        intact — it's part of the amount (thousand separator), not
        currency/amount delimiter."""
        self.assertEqual(
            normalize_currency_layout("$25 001,75"), "$ 25 001,75"
        )

    # ─── Defensive cases ──────────────────────────────

    def test_empty_string_passes_through(self):
        self.assertEqual(normalize_currency_layout(""), "")

    def test_unrecognized_format_passes_through(self):
        """Inputs that don't match any pattern fall through unchanged.
        Downstream will raise a parse error."""
        self.assertEqual(normalize_currency_layout("???"), "???")


class TestParseAmount(TestCase):
    # ─── US format (en_US — tried first) ──────────────

    def test_us_thousand_decimal(self):
        self.assertEqual(parse_amount("1,317.06"), 1317.06)

    def test_us_multiple_thousands(self):
        self.assertEqual(parse_amount("1,234,567.89"), 1234567.89)

    def test_us_simple_decimal(self):
        self.assertEqual(parse_amount("1317.06"), 1317.06)

    def test_us_integer(self):
        self.assertEqual(parse_amount("1317"), 1317.0)

    def test_us_negative(self):
        self.assertEqual(parse_amount("-0.07"), -0.07)

    # ─── EU format (de_DE — fallback) ─────────────────

    def test_eu_dot_thousand_comma_decimal(self):
        self.assertEqual(parse_amount("1.317,06"), 1317.06)

    def test_eu_simple_decimal(self):
        self.assertEqual(parse_amount("1317,06"), 1317.06)

    def test_eu_negative(self):
        self.assertEqual(parse_amount("-0,07"), -0.07)

    # ─── Whitespace handling ──────────────────────────

    def test_eu_space_thousand_stripped(self):
        """'1 317,06' — space as thousand separator, not recognized
        by de_DE CLDR; we pre-strip whitespace before parsing."""
        self.assertEqual(parse_amount("1 317,06"), 1317.06)

    def test_eu_nbsp_thousand_stripped(self):
        """Non-breaking space (U+00A0) as thousand separator — some
        European exports (including older Excel-generated CSVs) use
        this. Stripped like regular space."""
        self.assertEqual(parse_amount("1\xa0317,06"), 1317.06)

    # ─── Error paths ──────────────────────────────────

    def test_unparseable_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            parse_amount("abc")
        msg = str(ctx.exception)
        self.assertIn("en_US", msg)
        self.assertIn("de_DE", msg)
        self.assertIn("abc", msg)

    def test_empty_string_raises(self):
        with self.assertRaises(ValueError):
            parse_amount("")
