from collections import defaultdict
from typing import List, Dict
from loguru import logger

from domain.currency_exchange_service.currencies import FiatValue
from domain.transactions import Transaction, Action
from domain.stock.queue import Queue


def group_stock_trade_by_company(stock_transactions: List[Transaction]) -> Dict[str, List[Transaction]]:
    grouped_transactions = defaultdict(list)
    for transaction in stock_transactions:
        company_name = transaction.asset.asset_name
        grouped_transactions[company_name].append(transaction)
    return grouped_transactions


class PerStockProfitCalculator:
    EPSILON = 0.00000001

    def __init__(self, company: str):
        self.company = company

    def calculate_profit(self, transactions: List[Transaction]) -> (FiatValue, FiatValue):
        transactions.sort(key=lambda t: t.date)
        queue = Queue()
        cost, income = 0, 0

        logger.info(f"Calculating cost and income for company stock: {self.company}")
        logger.info(f"Number of transactions: {len(transactions)}")

        for transaction in transactions:
            if transaction.action == Action.BUY:
                queue.append(transaction, transaction.asset.amount)
                continue

            add_cost, add_income = self._handle_sell(queue, transaction)
            logger.debug(
                f"Calculated cost and income for transaction: {transaction}, cost = {add_cost}, income = {add_income}")
            cost += add_cost
            income += add_income

        return cost, income

    def _handle_sell(self, fifo_queue: Queue, transaction: Transaction) -> (FiatValue, FiatValue):
        quantity = transaction.asset.amount
        cost, income = FiatValue(0), FiatValue(0)

        while quantity > self.EPSILON:
            oldest_transaction = fifo_queue.head_item()
            oldest_transaction_quantity = fifo_queue.head_quantity()

            if oldest_transaction_quantity > quantity:
                cost += oldest_transaction.fiat_value * quantity
                income += transaction.fiat_value * quantity
                fifo_queue.reduce_quantity_head(quantity)
            else:
                cost += oldest_transaction.fiat_value * oldest_transaction_quantity
                income += transaction.fiat_value * oldest_transaction_quantity
                fifo_queue.pop_head()
            quantity -= oldest_transaction_quantity

        return cost, income
