from unittest import TestCase

from domain.currency_exchange_service.currencies import Currency, FiatValue, InvalidCurrencyException
from tests.utils import usd, zl


class TestFiatValue(TestCase):
    def test_add(self):
        a = usd(100)
        b = usd(200)

        self.assertEqual(a + b, FiatValue(300, Currency.DOLLAR))

    def test_add_different_currencies(self):
        a = usd(100)
        b = zl(200)

        with self.assertRaises(InvalidCurrencyException):
            a + b

    def test_mul(self):
        a = usd(100)

        self.assertEqual(a * 2, FiatValue(200, Currency.DOLLAR))

    def test_mul_by_non_numeric(self):
        a = usd(100)

        with self.assertRaises(ValueError):
            a * "a"

    def test_gt(self):
        a = usd(100)
        b = usd(200)

        self.assertTrue(b > a)

    def test_gt_different_currencies(self):
        a = usd(100)
        b = zl(200)

        with self.assertRaises(InvalidCurrencyException):
            a > b
