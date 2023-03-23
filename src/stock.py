from collections import defaultdict
from typing import List, Dict
import click

from data_sources.revolut.csv_reader import TransactionsCsvReader
from data_sources.revolut.stock.operation import OperationType
from data_sources.revolut.stock.operation_csv_parser import OperationStockCsvParser
from data_sources.revolut.stock.operations_csv_reader import OperationsCsvReader
from data_sources.revolut.stock.transaction_csv_parser import TransactionStockCsvParser
from domain.calendar_service.calendar import previous_year
from domain.stock.custody_fee import CustodyFee
from domain.stock.dividend import Dividend
from domain.stock.operation import Operation
from domain.stock.profit_calculator import YearlyPerStockProfitCalculator, group_transaction_by_company, \
    YearlyProfitCalculator
from domain.stock.stock_split import StockSplit
from domain.transactions import Transaction
from exchanger import create_exchanger


class StockSetup:

    @classmethod
    def setup_profit_calculator(cls) -> YearlyProfitCalculator:
        exchanger = create_exchanger()
        per_stock_calculator = YearlyPerStockProfitCalculator(exchanger)
        return YearlyProfitCalculator(exchanger, per_stock_calculator)

    @classmethod
    def read_transactions(cls, filepath: str) -> List:
        return TransactionsCsvReader(filepath, TransactionStockCsvParser).read()

    @classmethod
    def read_operations(cls, filepath: str) -> List:
        return OperationsCsvReader(filepath, OperationStockCsvParser).read()

    @classmethod
    def group_transactions_by_stock(cls, transactions: List[Transaction]) -> Dict[str, List[Transaction]]:
        return group_transaction_by_company(transactions)

    @classmethod
    def filter_stock_splits_and_group_by_stock(cls, operations: List[Operation]) -> Dict[str, List[StockSplit]]:
        stock_splits: List[StockSplit] = [operation for operation in operations if
                                          operation.type == OperationType.STOCK_SPLIT]
        stock_splits_by_stock: Dict[str, List[StockSplit]] = defaultdict(list)
        for stock_split in stock_splits:
            stock_splits_by_stock[stock_split.stock].append(stock_split)
        return stock_splits_by_stock

    @classmethod
    def filter_dividends(cls, operations: List[Operation]) -> List[Dividend]:
        return [operation for operation in operations if operation.type == OperationType.DIVIDEND]

    @classmethod
    def filter_stock_splits(cls, operations: List[Operation]) -> List[StockSplit]:
        return [operation for operation in operations if operation.type == OperationType.STOCK_SPLIT]

    @classmethod
    def filter_custody_fees(cls, operations: List[Operation]) -> List[CustodyFee]:
        return [operation for operation in operations if operation.type == OperationType.CUSTODY_FEE]


@click.command()
@click.option('--tax-year', '-y', default=previous_year(), help='Year you want to calculate tax for')
@click.option('--filepath', '-f',
              help='Path to csv file with transactions (currently only revolut csv format is supported)')
def stocks(tax_year: int, filepath: str):
    stock_setup = StockSetup()
    transactions = stock_setup.read_transactions(filepath)
    operations = stock_setup.read_operations(filepath)
    custody_fees = stock_setup.filter_custody_fees(operations)
    dividends = stock_setup.filter_dividends(operations)
    stock_splits = stock_setup.filter_stock_splits(operations)

    profit_calculator = stock_setup.setup_profit_calculator()
    profit_calculator.calculate_cumulative_cost_and_income(transactions, stock_splits, dividends, custody_fees)


if __name__ == "__main__":
    stocks()
