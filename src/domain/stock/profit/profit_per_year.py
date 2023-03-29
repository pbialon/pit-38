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

    def __add__(self, other):
        result = ProfitPerYear()
        years = set(self.income.keys()).union(set(other.income.keys()))
        for year in years:
            result.income[year] = self.income[year] + other.income[year]
            result.cost[year] = self.cost[year] + other.cost[year]
        return result

    def __eq__(self, other):
        return self.income == other.income and self.cost == other.cost
