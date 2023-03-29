from collections import defaultdict

from domain.currency_exchange_service.currencies import FiatValue


class ProfitPerYear:
    def __init__(self):
        self.income = defaultdict(lambda: FiatValue(0))
        self.cost = defaultdict(lambda: FiatValue(0))

    def add_income(self, year: int, value: FiatValue):
        self.income[year] += value

    def add_cost(self, year: int, value: FiatValue):
        self.cost[year] += value

    def get_income(self, year: int) -> FiatValue:
        return self.income[year]

    def get_cost(self, year: int) -> FiatValue:
        return self.cost[year]

    def all_years(self):
        return set(self.income.keys()).union(set(self.cost.keys()))

    def __add__(self, other):
        result = ProfitPerYear()
        all_years = self.all_years().union(other.all_years())
        for year in all_years:
            result.income[year] = self.income[year] + other.income[year]
            result.cost[year] = self.cost[year] + other.cost[year]
        return result

    def __eq__(self, other):
        return self.income == other.income and self.cost == other.cost

    def __str__(self):
        return "; ".join(
            f"[{year}]: +{self.income[year]} -{self.cost[year]}"
            for year in self.all_years()
        )
