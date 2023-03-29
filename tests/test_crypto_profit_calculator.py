from unittest import TestCase

from domain.crypto.profit_calculator import YearlyProfitCalculator
from domain.tax_service.profit_per_year import ProfitPerYear
from tests.utils import buy, sell, btc, usd, StubExchanger, zl


class TestYearlyProfitCalculator(TestCase):
    def test_profit_per_year(self):
        transactions = [
            buy(btc(1), usd(100), "2019-01-01"),
            sell(btc(1), usd(200), "2019-01-02"),
            buy(btc(1), usd(200), "2020-01-01"),
            sell(btc(1), usd(300), "2020-01-02"),
            buy(btc(1), usd(250), "2021-01-01"),
            sell(btc(1), usd(400), "2021-01-02"),
        ]
        yearly_profit_calculator = YearlyProfitCalculator(StubExchanger())
        profit_per_year = yearly_profit_calculator.profit_per_year(transactions)
        expected_profit_per_year = ProfitPerYear(
            income={
                2019: zl(800),
                2020: zl(1200),
                2021: zl(1600)
            }, cost={
                2019: zl(400),
                2020: zl(800),
                2021: zl(1000)
            }
        )

        self.assertEqual(profit_per_year, expected_profit_per_year)
