from collections import defaultdict
from typing import List, Dict

from currency_exchange_service.exchanger import Exchanger
from domain.crypto.profit_calculator import YearlyProfitCalculator
from domain.crypto.transaction import Transaction, Action


class TaxCalculator:
    def __init__(self, exchanger: Exchanger, yearly_calculator: YearlyProfitCalculator):
        self.exchanger = exchanger
        self.yearly_calculator = yearly_calculator

    def calculate_tax_per_year(self, transactions: List[Transaction], year: int):
        # assert all transactions are in the same currency
        assert len(set([t.crypto_value.currency for t in transactions])) == 1
        income = self.yearly_calculator.income_per_year(transactions)
        cost = self.yearly_calculator.cost_per_year(transactions)

        profit_before_tax_year = self.calculate_profit_before_tax_year(income, cost, year)
        profit_in_tax_year = income[year] - cost[year]
        if profit_before_tax_year < 0:
            profit_in_tax_year -= profit_before_tax_year

        return {
            year: {
                "income": income[year],
                "cost": cost[year]
            } for year in income.keys()
        }

    def deduct_loss_from_previous_years(self, income: Dict[int, float], cost: Dict[int, float], year: int):
        # todo: up to 5 years
        years = sorted(income.keys() | cost.keys())
        profit_per_year = {year: income[year] - cost[year] for year in years}

        accumulated_loss = 0
        for this_year in years:
            profit_this_year = profit_per_year[this_year]
            if profit_this_year >= accumulated_loss:
                # tax was paid and accumulated loss was taken into account
                accumulated_loss = 0
                continue
            accumulated_loss -= profit_this_year

        return accumulated_loss

    def calculate_profit_before_tax_year(self, income: Dict[int, float], cost: Dict[int, float], year: int):
        start_year = min(income.keys() | cost.keys())
        profit = 0
        while start_year < year:
            profit += income[start_year] - cost[start_year]
            start_year += 1
        return profit
