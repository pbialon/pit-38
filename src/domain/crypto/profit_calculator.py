from collections import defaultdict
from typing import List
from loguru import logger

from domain.currency_exchange_service.currencies import FiatValue
from domain.currency_exchange_service.exchanger import Exchanger
from domain.tax_service.profit_per_year import ProfitPerYear
from domain.transactions import Transaction, Action


class YearlyProfitCalculator:

    def __init__(self, exchanger: Exchanger):
        self.exchanger = exchanger

    def profit_per_year(self, transactions: List[Transaction], include_fees: bool) -> ProfitPerYear:
        income = self._sum_transactions_per_year(transactions, Action.SELL)
        cost = self._sum_transactions_per_year(transactions, Action.BUY)
        fees = self._sum_fees_per_year(transactions)
        profit = ProfitPerYear(income, cost)
        if include_fees:
            logger.info("Adding fees to the cost calculation")
            for year in fees.keys():
                profit.add_cost(year, fees[year])
        logger.info(f"Calculated profit per year: {profit}")
        return profit

    def _sum_transactions_per_year(self, transactions: List[Transaction], transaction_type: Action) \
            -> defaultdict[int, FiatValue]:
        transactions_sum_per_year: defaultdict[int, FiatValue] = defaultdict(lambda: FiatValue(0))
        for transaction in transactions:
            if transaction.action != transaction_type:
                continue
            transaction_value_in_base_currency = self.exchanger.exchange(
                transaction.date, transaction.fiat_value)
            transactions_sum_per_year[transaction.year()] += transaction_value_in_base_currency

        return transactions_sum_per_year

    def _sum_fees_per_year(self, transactions: List[Transaction]) -> defaultdict[int, FiatValue]:
        fees_sum_per_year: defaultdict[int, FiatValue] = defaultdict(lambda: FiatValue(0))
        for transaction in transactions:
            fees_sum_per_year[transaction.year()] += transaction.fees
        return fees_sum_per_year
