from collections import defaultdict

from domain.currency_exchange_service.currencies import FiatValue
from domain.tax_service.profit_per_year import ProfitPerYear
from domain.tax_service.tax_year_result import TaxYearResult


class TaxCalculator:
    def __init__(self, tax_rate: float = 0.19):
        self.tax_rate = tax_rate

    def calculate_tax_per_year(self,
                               profit_per_year: ProfitPerYear,
                               tax_year: int,
                               deductible_loss: float = -1) -> TaxYearResult:

        loss = self.deductible_loss_from_previous_years(
            profit_per_year, tax_year) if deductible_loss == -1 else FiatValue(deductible_loss)

        profit_in_tax_year = profit_per_year.get_profit(tax_year)
        if loss > FiatValue(0):
            profit_in_tax_year -= loss

        return TaxYearResult(
            tax_year,
            profit_per_year.get_income(tax_year),
            profit_per_year.get_cost(tax_year),
            loss,
            profit_in_tax_year,
            self.calculate_tax(profit_in_tax_year)
        )

    def calculate_tax(self, profit_in_tax_year: int):
        zero = FiatValue(0)
        return profit_in_tax_year * self.tax_rate if profit_in_tax_year > zero else zero


    def deductible_loss_from_previous_years(self,
                                            profit_per_year: ProfitPerYear,
                                            tax_year: int) -> FiatValue:

        accumulated_loss = FiatValue(0)
        # todo: up to 5 years (?)
        for year in self._years_before(tax_year, profit_per_year.all_years()):
            profit_this_year = profit_per_year.get_profit(year)
            if profit_this_year >= accumulated_loss:
                # tax was paid and accumulated loss was taken into account
                accumulated_loss = FiatValue(0)
                continue
            accumulated_loss -= profit_this_year

        return accumulated_loss

    def _years_before(self, tax_year: int, years: set[int]) -> set[int]:
        return {
            year
            for year in years
            if year < tax_year
        }