from typing import List
import click

from data_sources.revolut.csv_reader import TransactionsCsvReader as RevolutStockCsvReader
from data_sources.etrade.stock import StockCsvReader as EtradeStockCsvReader
from data_sources.revolut.stock.operation import OperationType
from data_sources.revolut.stock.operation_csv_parser import OperationStockCsvParser
from data_sources.revolut.stock.operations_csv_reader import OperationsCsvReader
from data_sources.revolut.stock.transaction_csv_parser import TransactionStockCsvParser
from domain.calendar_service.calendar import previous_year
from domain.stock.operations.custody_fee import CustodyFee
from domain.stock.operations.dividend import Dividend
from domain.stock.operations.operation import Operation
from domain.stock.profit.per_stock_calculator import PerStockProfitCalculator
from domain.stock.profit.profit_calculator import ProfitCalculator
from domain.stock.operations.stock_split import StockSplit
from domain.tax_service.tax_calculator import TaxCalculator
from exchanger import create_exchanger
from loguru import logger
import sys


class StockSetup:

    @classmethod
    def setup_profit_calculator(cls) -> ProfitCalculator:
        exchanger = create_exchanger()
        per_stock_calculator = PerStockProfitCalculator(exchanger)
        return ProfitCalculator(exchanger, per_stock_calculator)

    @classmethod
    def read_transactions(cls, revolut_filepath: str, etrade_filepath: str) -> List:
        etrade_transactions = EtradeStockCsvReader.read(etrade_filepath) if etrade_filepath else []
        revolut_transaction = RevolutStockCsvReader(revolut_filepath, TransactionStockCsvParser).read() if revolut_filepath else []
        
        return etrade_transactions + revolut_transaction

    @classmethod
    def read_operations(cls, filepath: str) -> List:
        return OperationsCsvReader(filepath, OperationStockCsvParser).read()

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
@click.option('--revolut',
              help='Path to csv file with transactions (currently only revolut csv format is supported)')
@click.option('--etrade', help='Path to csv file with transactions from ETRADE')
@click.option('--deductible-loss', '-l', default=-1,
              help='Deductible loss from previous years. It overrides calculation of loss by the script',
              type=float)
@click.option('--log-level', '-ll', default='DEBUG', help='Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
def stocks(tax_year: int, revolut: str, etrade: str, deductible_loss: float, log_level: str):
    # set log level
    logger.remove()
    logger.add(sys.stderr, level=log_level.upper())

    stock_setup = StockSetup()
    transactions = stock_setup.read_transactions(revolut, etrade)
    operations = stock_setup.read_operations(revolut)
    custody_fees = stock_setup.filter_custody_fees(operations)
    dividends = stock_setup.filter_dividends(operations)
    stock_splits = stock_setup.filter_stock_splits(operations)

    profit_calculator = stock_setup.setup_profit_calculator()
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
