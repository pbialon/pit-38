from collections import defaultdict
from typing import Dict

from domain.currency_exchange_service.currencies import FiatValue
from domain.tax_service.tax_year_result import TaxYearResult


class TaxCalculator:
    def __init__(self, tax_rate: float = 0.19):
        self.tax_rate = tax_rate

    def calculate_tax_per_year(self,
                               income_per_year: Dict[int, FiatValue],
                               cost_per_year: Dict[int, FiatValue],
                               tax_year: int,
                               deductible_loss: float = -1) -> TaxYearResult:

        loss: FiatValue = self.deductible_loss_from_previous_years(
            income_per_year, cost_per_year, tax_year
        ) if deductible_loss == -1 else FiatValue(deductible_loss)

        profit_in_tax_year: FiatValue = income_per_year[tax_year] - cost_per_year[tax_year]
        if loss > FiatValue(0):
            profit_in_tax_year -= loss

        tax = profit_in_tax_year * self.tax_rate if profit_in_tax_year > FiatValue(0) else FiatValue(0)
        return TaxYearResult(
            tax_year,
            income_per_year[tax_year],
            cost_per_year[tax_year],
            loss,
            profit_in_tax_year,
            tax
        )

    def deductible_loss_from_previous_years(self,
                                            income: defaultdict[int, FiatValue],
                                            cost: defaultdict[int, FiatValue],
                                            tax_year: int) -> FiatValue:
        # todo: up to 5 years
        years = {
            year
            for year in income.keys() | cost.keys()
            if year < tax_year
        }
        profit_per_year = {year: income[year] - cost[year] for year in years}

        accumulated_loss = FiatValue(0)
        for year in years:
            profit_this_year = profit_per_year[year]
            if profit_this_year >= accumulated_loss:
                # tax was paid and accumulated loss was taken into account
                accumulated_loss = FiatValue(0)
                continue
            accumulated_loss -= profit_this_year

        return accumulated_loss
