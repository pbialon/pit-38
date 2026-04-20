from pit38.domain.currency_exchange_service.currencies import FiatValue
from pit38.domain.tax_service.profit_per_year import ProfitPerYear
from pit38.domain.tax_service.tax_year_result import TaxYearResult


class CryptoTaxCalculator:
    """Crypto tax calculator per art. 22 ust. 16 — cost surplus carries
    forward without time or percentage limits."""

    def __init__(self, tax_rate: float = 0.19):
        self.tax_rate = tax_rate

    def calculate_tax_per_year(
        self,
        profit_per_year: ProfitPerYear,
        tax_year: int,
        deductible_loss: float = -1,
    ) -> TaxYearResult:
        if deductible_loss != -1:
            loss = FiatValue(deductible_loss)
        else:
            loss = self._deductible_loss(profit_per_year, tax_year)

        profit_in_tax_year = profit_per_year.get_profit(tax_year)
        if loss > FiatValue(0):
            profit_in_tax_year = profit_in_tax_year - loss

        return TaxYearResult(
            tax_year,
            profit_per_year.get_income(tax_year),
            profit_per_year.get_cost(tax_year),
            loss,
            profit_in_tax_year,
            self._calculate_tax(profit_in_tax_year),
        )

    def _deductible_loss(
        self, profit_per_year: ProfitPerYear, tax_year: int
    ) -> FiatValue:
        accumulated_loss = FiatValue(0)
        for year in sorted(y for y in profit_per_year.all_years() if y < tax_year):
            profit_this_year = profit_per_year.get_profit(year)
            if profit_this_year >= accumulated_loss:
                accumulated_loss = FiatValue(0)
                continue
            accumulated_loss = accumulated_loss - profit_this_year
        return accumulated_loss

    def _calculate_tax(self, profit: FiatValue) -> FiatValue:
        zero = FiatValue(0)
        return profit * self.tax_rate if profit > zero else zero
