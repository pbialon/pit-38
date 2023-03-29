from collections import defaultdict
from typing import List, Dict

from loguru import logger

from domain.currency_exchange_service.currencies import FiatValue
from domain.stock.operations.custody_fee import CustodyFee
from domain.stock.operations.dividend import Dividend
from domain.stock.operations.stock_split import StockSplit
from domain.stock.profit.per_stock_calculator import PerStockProfitCalculator
from domain.stock.profit.profit_per_year import ProfitPerYear
from domain.stock.profit.stock_split_handler import StockSplitHandler
from domain.transactions import Transaction


class ProfitCalculator:
    def __init__(self, exchanger, per_stock_calculator: PerStockProfitCalculator):
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
        profit = ProfitPerYear()
        stock_splits_by_company = self._group_stock_split_by_stock(stock_splits)

        for company, transactions in self._group_transaction_by_stock(transactions).items():
            transactions_adjusted = StockSplitHandler.incorporate_stock_splits_into_transactions(
                transactions, stock_splits_by_company[company])
            profit += self.per_stock_calculator.calculate_cost_and_income(transactions_adjusted)

        logger.info("Processing dividends")
        for dividend in dividends:
            income = self.exchanger.exchange(dividend.date, dividend.value)
            profit.add_income(dividend.date.year, income)

        logger.info("Processing custody fees")
        for custody_fees in custody_fees:
            cost = self.exchanger.exchange(custody_fees.date, custody_fees.value)
            profit.add_cost(custody_fees.date.year, cost)

        logger.info(f"Profit per year: {profit}")

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
