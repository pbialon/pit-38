from collections import defaultdict
from typing import List, Dict

from loguru import logger

from domain.currency_exchange_service.currencies import FiatValue
from domain.stock.operations.custody_fee import CustodyFee
from domain.stock.operations.dividend import Dividend
from domain.stock.operations.stock_split import StockSplit
from domain.stock.profit.per_stock_calculator import PerStockProfitCalculator
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
        stock_splits_by_company = self._group_stock_split_by_stock(stock_splits)
        for company, transactions in self._group_transaction_by_stock(transactions).items():
            cost, income = self.per_stock_calculator.calculate_cost_and_income(
                transactions, stock_splits_by_company[company])
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
