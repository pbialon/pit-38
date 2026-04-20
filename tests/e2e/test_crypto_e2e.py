"""End-to-end tests for the crypto tax pipeline.

Tests the full flow: standardized CSV → loader → profit calculator →
crypto tax calculator → final result.
"""
import pathlib
from unittest import TestCase

from pit38.data_sources.crypto_loader.csv_loader import Loader as CryptoLoader
from pit38.domain.crypto.profit_calculator import YearlyProfitCalculator
from pit38.domain.tax_service.crypto_tax_calculator import CryptoTaxCalculator
from tests.utils import StubExchanger

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


class TestCryptoFullPipeline(TestCase):

    def test_standardized_csv_to_tax_result(self):
        csv_path = FIXTURES / "standardized_crypto.csv"

        transactions = CryptoLoader.load(str(csv_path))
        self.assertEqual(len(transactions), 5)

        exchanger = StubExchanger()
        profit_calc = YearlyProfitCalculator(exchanger)
        profit = profit_calc.profit_per_year(transactions)

        tax_calc = CryptoTaxCalculator()

        # 2023: buy BTC 16K + buy ETH 16K (costs), sell BTC 9K (income)
        # All PLN so StubExchanger passes through
        result_2023 = tax_calc.calculate_tax_per_year(profit, 2023)
        self.assertEqual(result_2023.income.amount, 9000)
        self.assertEqual(result_2023.cost.amount, 32000)
        self.assertEqual(result_2023.tax.amount, 0)

        # 2024: sell ETH 10K + sell BTC 10K (income), no buys (cost=0)
        # Loss from 2023 = 23000, carried forward without limit
        result_2024 = tax_calc.calculate_tax_per_year(profit, 2024)
        self.assertEqual(result_2024.income.amount, 20000)
        self.assertEqual(result_2024.cost.amount, 0)
        self.assertEqual(result_2024.deductible_loss.amount, 23000)
        self.assertEqual(result_2024.tax.amount, 0)

    def test_crypto_cost_only_year(self):
        csv_path = FIXTURES / "standardized_crypto_buy_only.csv"

        transactions = CryptoLoader.load(str(csv_path))

        exchanger = StubExchanger()
        profit_calc = YearlyProfitCalculator(exchanger)
        profit = profit_calc.profit_per_year(transactions)

        tax_calc = CryptoTaxCalculator()
        result = tax_calc.calculate_tax_per_year(profit, 2023)

        self.assertGreater(result.cost.amount, 0)
        self.assertEqual(result.income.amount, 0)
        self.assertEqual(result.tax.amount, 0)
