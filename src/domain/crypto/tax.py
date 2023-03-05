from collections import defaultdict
from typing import List

from currency_exchange_service.currencies import Currency
from currency_exchange_service.exchanger import Exchanger
from domain.crypto.transaction import Transaction


class TaxCalculator:
    def __init__(self, exchanger: Exchanger, base_currency: Currency = Currency.PLN):
        self.exchanger = exchanger
        self.base_currency = base_currency

    def calculate(self, transactions: List[Transaction], year: int):
        # assert all transactions are in the same currency
        assert len(set([t.crypto_value.currency for t in transactions])) == 1

        # calculate tax

    def income_per_year(self, transactions: List[Transaction]):
        income_per_year = defaultdict(float)
        for transaction in transactions:
            if transaction.action == Transaction.Action.BUY:
                continue
            transaction_value_in_base_currency = self.exchanger.exchange(
                transaction.fiat_value, transaction.fiat_value, self.base_currency)

            income_per_year[transaction.date.year] += transaction.crypto_value.value




    def cost_per_year(self, transactions: List[Transaction]):
        # calculate cost per year
        pass