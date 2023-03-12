from typing import List, Dict

from domain.crypto.profit_calculator import YearlyProfitCalculator
from domain.crypto.transaction import Transaction


class TaxYearResult:
    def __init__(self,
                 tax_year: int,
                 income: int,
                 cost: int,
                 deductable_loss: int,
                 base_for_tax: int,
                 tax: float):
        self.tax_year = tax_year
        self.income = income
        self.cost = cost
        self.deductable_loss = deductable_loss
        self.base_for_tax = base_for_tax
        self.tax = tax


def __str__(self):
    return f"[{self.tax_year}]: \n" \
           f"income: +{self.income} ZŁ, outcome -{self.cost}\n" \
           f"deductable loss: {self.deductable_loss} ZŁ\n" \
           f"base for tax: {self.base_for_tax} ZŁ\n" \
           f"tax: {self.tax} ZŁ"


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
        return TaxYearResult(tax_year, income[tax_year], cost[tax_year], loss, profit_in_tax_year, tax)

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
