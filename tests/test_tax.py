from unittest import TestCase

from domain.crypto.tax import TaxCalculator


class StubExchanger:
    def exchange(self, date, fiat_value):
        return fiat_value


class TestTaxCalculator(TestCase):
    def test_calculate(self):
        tax_calculator = TaxCalculator(StubExchanger())
        tax_calculator.calculate([], 2020)
        self.fail()
