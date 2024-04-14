from unittest import TestCase
from data_sources.etrade.fiat_value_parser import FiatValueParser, Currency, FiatValue


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