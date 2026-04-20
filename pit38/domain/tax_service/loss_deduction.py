from dataclasses import dataclass, field
from typing import List

from pit38.domain.currency_exchange_service.currencies import FiatValue
from pit38.domain.tax_service.profit_per_year import ProfitPerYear

FIVE_MILLION = FiatValue(5_000_000)
ZERO = FiatValue(0)


@dataclass
class LossRecord:
    year: int
    original_amount: FiatValue
    already_deducted: FiatValue = field(default_factory=FiatValue)

    @property
    def remaining(self) -> FiatValue:
        return self.original_amount - self.already_deducted

    def is_expired(self, tax_year: int) -> bool:
        return tax_year - self.year > 5

    def max_deductible_this_year(self, tax_year: int) -> FiatValue:
        if self.is_expired(tax_year):
            return ZERO
        remaining = self.remaining
        if remaining <= ZERO:
            return ZERO
        if self.year >= 2019 and remaining <= FIVE_MILLION:
            return remaining
        fifty_pct = self.original_amount * 0.5
        if remaining <= fifty_pct:
            return remaining
        return fifty_pct


class StockLossDeductionStrategy:
    def calculate_deductible_loss(
        self, profit_per_year: ProfitPerYear, tax_year: int
    ) -> FiatValue:
        losses = self._collect_losses(profit_per_year, tax_year)
        profit = profit_per_year.get_profit(tax_year)
        if profit <= ZERO:
            return ZERO

        total_deducted = FiatValue(0)
        remaining_profit = profit

        for loss in losses:
            max_this = loss.max_deductible_this_year(tax_year)
            if max_this <= ZERO:
                continue
            to_deduct = max_this if max_this <= remaining_profit else remaining_profit
            loss.already_deducted = loss.already_deducted + to_deduct
            total_deducted = total_deducted + to_deduct
            remaining_profit = remaining_profit - to_deduct
            if remaining_profit <= ZERO:
                break

        return total_deducted

    def _collect_losses(
        self, profit_per_year: ProfitPerYear, tax_year: int
    ) -> List[LossRecord]:
        losses = []
        for year in sorted(profit_per_year.all_years()):
            if year >= tax_year:
                continue
            year_profit = profit_per_year.get_profit(year)
            if year_profit < ZERO:
                loss_amount = year_profit * -1
                losses.append(LossRecord(year=year, original_amount=loss_amount))
        return losses
