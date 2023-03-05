from collections import defaultdict
from typing import List, Dict

from currency_exchange_service.exchanger import Exchanger
from domain.crypto.transaction import Transaction, Action


class YearlyProfitCalculator:

    def __init__(self, exchanger: Exchanger):
        self.exchanger = exchanger

    def income_per_year(self, transactions: List[Transaction]) -> Dict[int, float]:
        return self._sum_transactions_per_year(transactions, Action.SELL)

    def cost_per_year(self, transactions: List[Transaction]) -> Dict[int, float]:
        return self._sum_transactions_per_year(transactions, Action.BUY)

    def _sum_transactions_per_year(self, transactions: List[Transaction], transaction_type: Action) -> Dict[int, float]:
        transactions_sum_per_year = defaultdict(list)
        for transaction in transactions:
            if transaction.action != transaction_type:
                continue
            transaction_value_in_base_currency = self.exchanger.exchange(
                transaction.date, transaction.fiat_value)
            transactions_sum_per_year[transaction.date.year] += transaction_value_in_base_currency.amount

        return transactions_sum_per_year
