from collections import defaultdict
from typing import List
from loguru import logger

from domain.currency_exchange_service.currencies import FiatValue
from domain.currency_exchange_service.exchanger import Exchanger
from domain.crypto.transaction import Transaction, Action


class YearlyProfitCalculator:

    def __init__(self, exchanger: Exchanger):
        self.exchanger = exchanger

    def income_per_year(self, transactions: List[Transaction]) -> defaultdict[int, FiatValue]:
        income = self._sum_transactions_per_year(transactions, Action.SELL)
        logger.info(f"Calculated income per year: {dict(income)}")
        return income

    def cost_per_year(self, transactions: List[Transaction]) -> defaultdict[int, FiatValue]:
        cost = self._sum_transactions_per_year(transactions, Action.BUY)
        logger.info(f"Calculated cost per year: {dict(cost)}")
        return cost

    def _sum_transactions_per_year(self, transactions: List[Transaction], transaction_type: Action) \
            -> defaultdict[int, FiatValue]:
        transactions_sum_per_year: defaultdict[int, FiatValue] = defaultdict(lambda: FiatValue(0))
        for transaction in transactions:
            if transaction.action != transaction_type:
                continue
            transaction_value_in_base_currency = self.exchanger.exchange(
                transaction.date, transaction.fiat_value)
            transactions_sum_per_year[transaction.date.year] += transaction_value_in_base_currency

        return transactions_sum_per_year
