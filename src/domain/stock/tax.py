from typing import Dict

from domain.crypto.profit_calculator import YearlyProfitCalculator
from domain.currency_exchange_service.currencies import FiatValue
from domain.transactions import Transaction


class TaxCalculator:
    def __init__(self, profit_calculator: YearlyProfitCalculator):
        self.profit_calculator = profit_calculator

    def calculate_tax(self,
                      year: int,
                      cost_per_year: Dict[int, FiatValue],
                      income_per_year: Dict[int, FiatValue]) -> FiatValue:

        pass
