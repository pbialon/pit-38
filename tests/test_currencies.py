from unittest import TestCase

from domain.currency_exchange_service.currencies import Currency, FiatValue, InvalidCurrencyException


class TestFiatValue(TestCase):
    def test_add(self):
        a = FiatValue(100, Currency.DOLLAR)
        b = FiatValue(200, Currency.DOLLAR)

        self.assertEqual(a + b, FiatValue(300, Currency.DOLLAR))

    def test_add_different_currencies(self):
        a = FiatValue(100, Currency.DOLLAR)
        b = FiatValue(200, Currency.ZLOTY)

        with self.assertRaises(InvalidCurrencyException):
            a + b

    def test_mul(self):
        a = FiatValue(100, Currency.DOLLAR)

        self.assertEqual(a * 2, FiatValue(200, Currency.DOLLAR))

    def test_mul_by_non_numeric(self):
        a = FiatValue(100, Currency.DOLLAR)

        with self.assertRaises(ValueError):
            a * "a"

    def test_gt(self):
        a = FiatValue(100, Currency.DOLLAR)
        b = FiatValue(200, Currency.DOLLAR)

        self.assertTrue(b > a)

    def test_gt_different_currencies(self):
        a = FiatValue(100, Currency.DOLLAR)
        b = FiatValue(200, Currency.ZLOTY)

        with self.assertRaises(InvalidCurrencyException):
            a > b
