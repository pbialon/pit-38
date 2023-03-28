from collections import defaultdict
from typing import List, Dict

import pendulum
from loguru import logger

from domain.currency_exchange_service.currencies import FiatValue
from domain.currency_exchange_service.exchanger import Exchanger
from domain.stock.operations.custody_fee import CustodyFee
from domain.stock.operations.dividend import Dividend
from domain.stock.operations.stock_split import StockSplit
from domain.transactions import Transaction, Action
from domain.stock.queue import Queue


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

    def calculate_cost_and_income(self,
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
                queue.append(transaction)
                continue

            transaction_cost = self._calculate_cost_for_sell(queue, transaction)
            transaction_income = self.exchanger.exchange(transaction.date, transaction.fiat_value)
            transaction_profit = transaction_income - transaction_cost
            logger.debug(
                f"Calculated cost and income for transaction: {transaction}, "
                f"cost = {transaction_cost}, income = {transaction_income}, profit = {transaction_profit}")
            year = transaction.date.year
            cost[year] += transaction_cost
            income[year] += transaction_income

        for year in cost.keys():
            profit = income[year] - cost[year]
            logger.info(f"Year: {year} for {self._get_company_name(transactions)}, "
                        f"cost: {cost[year]}, income: {income[year]}, profit: {profit}")

        return cost, income

    def _calculate_cost_for_sell(self, buy_queue: Queue, transaction: Transaction) -> FiatValue:
        stock_amount_to_account = transaction.asset.amount
        cost = FiatValue(0)

        while stock_amount_to_account > self.EPSILON:
            oldest_buy = buy_queue.head()
            oldest_buy_stock_amount = oldest_buy.asset.amount

            if oldest_buy_stock_amount <= stock_amount_to_account + self.EPSILON:
                cost += self.exchanger.exchange(oldest_buy.date, oldest_buy.fiat_value)
                stock_amount_to_account -= oldest_buy_stock_amount
                buy_queue.pop_head()
            else:
                ratio_of_oldest_buy_to_include = stock_amount_to_account / oldest_buy_stock_amount
                cost += self.exchanger.exchange(
                    transaction.date, oldest_buy.fiat_value) * ratio_of_oldest_buy_to_include
                stock_amount_to_account = 0
                new_head = buy_queue.head() * (1 - ratio_of_oldest_buy_to_include)
                buy_queue.replace_head(new_head)

        return cost

    def _ratio_of_transaction_to_include(self, oldest_transaction_quantity: float, quantity: float) -> float:
        if oldest_transaction_quantity > quantity:
            return quantity / oldest_transaction_quantity
        return 1


class YearlyProfitCalculator:
    def __init__(self, exchanger, per_stock_calculator: YearlyPerStockProfitCalculator):
        self.exchanger = exchanger
        self.per_stock_calculator = per_stock_calculator

    def calculate_cumulative_cost_and_income(
            self,
            transactions: List[Transaction],
            stock_splits: List[StockSplit],
            dividends: List[Dividend],
            custody_fees: List[CustodyFee]) -> (FiatValue, FiatValue):

        cost_by_year = defaultdict(lambda: FiatValue(0))
        income_by_year = defaultdict(lambda: FiatValue(0))
        for company, transactions in self._group_transaction_by_stock(transactions).items():
            cost, income = self.per_stock_calculator.calculate_cost_and_income(transactions, stock_splits)
            for year in cost.keys():
                cost_by_year[year] += cost[year]
                income_by_year[year] += income[year]

        for dividend in dividends:
            profit = self.exchanger.exchange(dividend.date, dividend.value)
            logger.debug(f"Processing dividend {dividend}, profit: {profit}")
            income_by_year[dividend.date.year] += profit

        for custody_fees in custody_fees:
            cost = self.exchanger.exchange(custody_fees.date, custody_fees.value)
            logger.debug(f"Processing custody fees {custody_fees}, cost: {cost}")
            cost_by_year[custody_fees.date.year] += cost

        for year in cost_by_year.keys():
            logger.info(f"Year: {year}, cost: {cost_by_year[year]}, income: {income_by_year[year]}")

        return cost_by_year, income_by_year

    def _group_transaction_by_stock(self, transactions: List[Transaction]) -> Dict[str, List[Transaction]]:
        grouped_transactions = defaultdict(list)
        for transaction in transactions:
            company_name = transaction.asset.asset_name
            grouped_transactions[company_name].append(transaction)
        return grouped_transactions

    def _group_stock_split_by_stock(self, stock_splits: List[StockSplit]) -> Dict[str, List[StockSplit]]:
        stock_splits_by_stock = defaultdict(list)
        for stock_split in stock_splits:
            stock_splits_by_stock[stock_split.stock].append(stock_split)
        return stock_splits_by_stock
