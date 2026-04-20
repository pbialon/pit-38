from unittest import TestCase

from pit38.domain.currency_exchange_service.currencies import Currency, FiatValue
from pit38.plugins.stock.revolut.row_parser import RowParser


class TestFiatValueParsing(TestCase):
    def test_old_format_usd(self):
        row = {'Total Amount': '$500', 'Currency': 'USD'}
        self.assertEqual(RowParser._fiat_value(row), FiatValue(500, Currency.DOLLAR))

    def test_old_format_usd_with_comma(self):
        row = {'Total Amount': '$1,003.01', 'Currency': 'USD'}
        self.assertEqual(RowParser._fiat_value(row), FiatValue(1003.01, Currency.DOLLAR))

    def test_old_format_negative(self):
        row = {'Total Amount': '-$529.68', 'Currency': 'USD'}
        self.assertEqual(RowParser._fiat_value(row), FiatValue(529.68, Currency.DOLLAR))

    def test_old_format_eur(self):
        row = {'Total Amount': '€250.00', 'Currency': 'EUR'}
        self.assertEqual(RowParser._fiat_value(row), FiatValue(250, Currency.EURO))

    def test_new_format_usd(self):
        row = {'Total Amount': 'USD 1317.06', 'Currency': 'USD'}
        self.assertEqual(RowParser._fiat_value(row), FiatValue(1317.06, Currency.DOLLAR))

    def test_new_format_eur(self):
        row = {'Total Amount': 'EUR 500.00', 'Currency': 'EUR'}
        self.assertEqual(RowParser._fiat_value(row), FiatValue(500, Currency.EURO))

    def test_new_format_negative(self):
        row = {'Total Amount': '-USD 529.68', 'Currency': 'USD'}
        self.assertEqual(RowParser._fiat_value(row), FiatValue(529.68, Currency.DOLLAR))

    def test_new_format_with_comma(self):
        row = {'Total Amount': 'USD 1,317.06', 'Currency': 'USD'}
        self.assertEqual(RowParser._fiat_value(row), FiatValue(1317.06, Currency.DOLLAR))

    def test_currency_mismatch_raises_error(self):
        row = {'Total Amount': '$500', 'Currency': 'EUR'}
        with self.assertRaises(ValueError) as ctx:
            RowParser._fiat_value(row)
        self.assertIn("Currency mismatch", str(ctx.exception))

    def test_missing_currency_column(self):
        row = {'Total Amount': 'USD 1317.06'}
        self.assertEqual(RowParser._fiat_value(row), FiatValue(1317.06, Currency.DOLLAR))

    def test_empty_currency_column(self):
        row = {'Total Amount': 'EUR 500.00', 'Currency': ''}
        self.assertEqual(RowParser._fiat_value(row), FiatValue(500, Currency.EURO))

    def test_unparseable_amount_raises_error(self):
        row = {'Total Amount': '???', 'Currency': 'USD'}
        with self.assertRaises(ValueError) as ctx:
            RowParser._fiat_value(row)
        self.assertIn("Cannot parse Total Amount", str(ctx.exception))
