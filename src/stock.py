from typing import List
import click

from domain.calendar_service.calendar import previous_year
from domain.stock.operations.custody_fee import CustodyFee
from domain.stock.operations.dividend import Dividend
from domain.stock.operations.operation import Operation, OperationType
from domain.stock.profit.per_stock_calculator import PerStockProfitCalculator
from domain.stock.profit.profit_calculator import ProfitCalculator
from domain.stock.operations.stock_split import StockSplit
from domain.tax_service.tax_calculator import TaxCalculator
from domain.transactions.transaction import Transaction
from exchanger import create_exchanger
from loguru import logger
import sys
from data_sources.stock_loader.multi_sources_loader import MultiSourcesLoader
from data_sources.stock_loader.csv_loader import Loader as StockLoader

class StockSetup:

    @classmethod
    def setup_profit_calculator(cls) -> ProfitCalculator:
        exchanger = create_exchanger()
        per_stock_calculator = PerStockProfitCalculator(exchanger)
        return ProfitCalculator(exchanger, per_stock_calculator)
    
    @classmethod
    def set_log_level(cls, log_level: str):
        logger.remove()
        logger.add(sys.stderr, level=log_level.upper())
    
    @classmethod
    def read_all(cls, filepaths: tuple[str, ...]) -> List[Operation | Transaction]:
        return MultiSourcesLoader(StockLoader).load(filepaths)

    @classmethod
    def read_transactions(cls, records: List[Operation | Transaction]) -> List[Transaction]:
        return [record for record in records if isinstance(record, Transaction)]
    
    @classmethod
    def read_operations(cls, records: List[Operation | Transaction]) -> List[Operation]:
        return [record for record in records if isinstance(record, Operation)]

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
@click.option('--filepaths', '-f', multiple=True, required=True,
              help='Paths to csv files with transactions')
@click.option('--deductible-loss', '-l', default=-1,
              help='Deductible loss from previous years. It overrides calculation of loss by the script',
              type=float)
@click.option('--log-level', '-ll', default='DEBUG', help='Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
def stocks(tax_year: int, filepaths: tuple[str, ...], deductible_loss: float, log_level: str):
    StockSetup.set_log_level(log_level)

    records = StockSetup.read_all(filepaths)
    transactions = StockSetup.read_transactions(records)
    operations = StockSetup.read_operations(records)

    custody_fees = StockSetup.filter_custody_fees(operations)
    dividends = StockSetup.filter_dividends(operations)
    stock_splits = StockSetup.filter_stock_splits(operations)

    profit_calculator = StockSetup.setup_profit_calculator()
    profit_from_transactions, profit_from_dividends = profit_calculator.calculate_cumulative_cost_and_income(
        transactions, stock_splits, dividends, custody_fees)

    tax_calculator = TaxCalculator()
    tax_data_from_transactions = tax_calculator.calculate_tax_per_year(
        profit_from_transactions, tax_year, deductible_loss)
    tax_data_from_dividends = tax_calculator.calculate_tax_per_year(
        profit_from_dividends, tax_year, 0)

    print("\n\nTransactions: ", tax_data_from_transactions, end='\n\n')
    print("Dividends (if you paid 30% in USA you don't have to pay):", tax_data_from_dividends, end='\n\n')


if __name__ == "__main__":
    stocks()
