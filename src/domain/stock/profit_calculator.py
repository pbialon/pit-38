from collections import defaultdict
from typing import List, Dict

import pendulum
from loguru import logger

from domain.currency_exchange_service.currencies import FiatValue
from domain.currency_exchange_service.exchanger import Exchanger
from domain.stock.operation import Operation
from domain.stock.stock_split import StockSplit
from domain.transactions import Transaction, Action
from domain.stock.queue import Queue, TransactionWithQuantity


def group_transaction_by_company(transactions: List[Transaction]) -> Dict[str, List[Transaction]]:
    grouped_transactions = defaultdict(list)
    for transaction in transactions:
        company_name = transaction.asset.asset_name
        grouped_transactions[company_name].append(transaction)
    return grouped_transactions


class StockSplitHandler:
    @classmethod
    def multiplier_for_date(cls, stock_splits: List[StockSplit], date: pendulum.DateTime) -> float:
        assert sorted(stock_splits) == stock_splits, "It should be sorted"

        multiplier = 1
        for stock_split in reversed(stock_splits):
            if stock_split.date > date:
                multiplier *= stock_split.ratio
        if multiplier > 1:
            logger.debug(f"Stock split multiplier for {date} is {multiplier}")
        return multiplier


class YearlyPerStockProfitCalculator:
    EPSILON = 0.00000001

    def __init__(self, exchanger: Exchanger):
        self.exchanger = exchanger

    def _get_company_name(self, transaction: List[Transaction]) -> str:
        # check all transactions are from the same company
        assert (t.asset.asset_name == transaction[0].asset.asset_name for t in transaction), \
            "All transactions should be from the same company"
        return transaction[0].asset.asset_name

    def _stock_splits_into_transactions(self,
                                        stock_splits: List[StockSplit],
                                        transactions: List[Transaction]) -> List[Transaction]:
        stock_splits.sort(key=lambda s: s.date)
        transactions.sort(key=lambda t: t.date)

        new_transactions = []
        for transaction in transactions:
            multiplier = StockSplitHandler.multiplier_for_date(stock_splits, transaction.date)
            new_transactions.append(Transaction(
                transaction.asset * multiplier,
                transaction.fiat_value,
                transaction.action,
                transaction.date,
            ))

        return new_transactions

    def calculate_profit(self,
                         transactions: List[Transaction],
                         stock_splits: List[StockSplit]) -> (FiatValue, FiatValue):
        transactions.sort(key=lambda t: t.date)
        if stock_splits:
            logger.info(f"Handling {len(stock_splits)} stock splits")
            transactions = self._stock_splits_into_transactions(stock_splits, transactions)
            logger.debug(f"Transactions after handling stock splits: {transactions}")

        queue = Queue()
        cost = defaultdict(lambda: FiatValue(0))
        income = defaultdict(lambda: FiatValue(0))

        logger.info(f"Calculating cost and income for company stock: {self._get_company_name(transactions)}")
        logger.info(f"Number of transactions: {len(transactions)}")
        if stock_splits:
            logger.info(f"Stock splits: {stock_splits}")

        for transaction in transactions:
            if transaction.action == Action.BUY:
                queue.append(TransactionWithQuantity(transaction))
                continue

            add_cost, add_income = self._handle_sell(queue, transaction)
            logger.debug(
                f"Calculated cost and income for transaction: {transaction}, "
                f"cost = {add_cost}, income = {add_income}, profit = {add_income - add_cost}")
            year = transaction.date.year
            cost[year] += add_cost
            income[year] += add_income

        return cost, income

    def _handle_sell(self, fifo_queue: Queue, transaction: Transaction) -> (FiatValue, FiatValue):
        quantity = transaction.asset.amount
        cost, income = FiatValue(0), FiatValue(0)

        while quantity > self.EPSILON:
            oldest_transaction = fifo_queue.head_item()
            oldest_transaction_quantity = fifo_queue.head_quantity()

            if oldest_transaction_quantity > quantity:
                fifo_queue.reduce_quantity_head(quantity)
            else:
                fifo_queue.pop_head()

            ratio = self._ratio_of_transaction_to_include(oldest_transaction_quantity, quantity)
            cost += self.exchanger.exchange(oldest_transaction.date, oldest_transaction.fiat_value) * ratio
            income += self.exchanger.exchange(transaction.date, transaction.fiat_value) * ratio

            quantity -= oldest_transaction_quantity

        return cost, income

    def _ratio_of_transaction_to_include(self, oldest_transaction_quantity: float, quantity: float) -> float:
        if oldest_transaction_quantity > quantity:
            return quantity / oldest_transaction_quantity
        return 1
