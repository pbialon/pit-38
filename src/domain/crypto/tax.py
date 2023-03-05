from typing import List, Dict

from domain.crypto.profit_calculator import YearlyProfitCalculator
from domain.crypto.transaction import Transaction


class TaxCalculator:
    def __init__(self, yearly_calculator: YearlyProfitCalculator, tax_rate: float = 0.19):
        self.yearly_calculator = yearly_calculator
        self.tax_rate = tax_rate

    def calculate_tax_per_year(self, transactions: List[Transaction], tax_year: int):
        assert len(set([t.crypto_value.currency for t in transactions])) == 1
        income = self.yearly_calculator.income_per_year(transactions)
        cost = self.yearly_calculator.cost_per_year(transactions)

        loss = self.deductable_loss_from_previous_years(income, cost, tax_year)
        profit_in_tax_year = income[tax_year] - cost[tax_year]
        if loss > 0:
            profit_in_tax_year -= loss

        tax = profit_in_tax_year * self.tax_rate if profit_in_tax_year > 0 else 0
        return tax

    def deductable_loss_from_previous_years(self, income: Dict[int, float], cost: Dict[int, float], tax_year: int):
        # todo: up to 5 years
        years = {
            year
            for year in income.keys() | cost.keys()
            if year < tax_year
        }
        profit_per_year = {year: income[year] - cost[year] for year in years}

        accumulated_loss = 0
        for year in years:
            profit_this_year = profit_per_year[year]
            if profit_this_year >= accumulated_loss:
                # tax was paid and accumulated loss was taken into account
                accumulated_loss = 0
                continue
            accumulated_loss -= profit_this_year

        return accumulated_loss
