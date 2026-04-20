from typing import List
import click
import sys
from loguru import logger

from pit38.data_sources.stock_loader.csv_loader import Loader as StockLoader
from pit38.data_sources.stock_loader.multi_sources_loader import MultiSourcesLoader
from pit38.domain.calendar_service.calendar import previous_year
from pit38.domain.stock.operations.dividend import Dividend
from pit38.domain.stock.operations.operation import Operation, OperationType
from pit38.domain.stock.operations.service_fee import ServiceFee
from pit38.domain.stock.operations.stock_split import StockSplit
from pit38.domain.stock.profit.per_stock_calculator import PerStockProfitCalculator
from pit38.domain.stock.profit.profit_calculator import ProfitCalculator
from pit38.domain.tax_service.stock_tax_calculator import StockTaxCalculator
from pit38.domain.transactions.transaction import Transaction
from pit38.exchanger import create_exchanger
from pit38.output import print_stock_result

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
    def filter_transactions(cls, operations: List[Operation | Transaction]) -> List[Transaction]:
        return [operation for operation in operations if operation.type in [OperationType.BUY, OperationType.SELL]]

    @classmethod
    def filter_stock_splits(cls, operations: List[Operation]) -> List[StockSplit]:
        return [operation for operation in operations if operation.type == OperationType.STOCK_SPLIT]

    @classmethod
    def filter_dividends(cls, operations: List[Operation]) -> List[Dividend]:
        return [operation for operation in operations if operation.type == OperationType.DIVIDEND]

    @classmethod
    def filter_service_fees(cls, operations: List[Operation]) -> List[ServiceFee]:
        return [operation for operation in operations if operation.type == OperationType.SERVICE_FEE]



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

    service_fees = StockSetup.filter_service_fees(operations)
    dividends = StockSetup.filter_dividends(operations)
    stock_splits = StockSetup.filter_stock_splits(operations)

    profit_calculator = StockSetup.setup_profit_calculator()
    profit_from_transactions, profit_from_dividends = profit_calculator.calculate_cumulative_cost_and_income(
        transactions, stock_splits, dividends, service_fees)

    tax_calculator = StockTaxCalculator()
    tax_data_from_transactions = tax_calculator.calculate_tax_per_year(
        profit_from_transactions, tax_year, deductible_loss)
    tax_data_from_dividends = tax_calculator.calculate_tax_per_year(
        profit_from_dividends, tax_year, 0)

    print_stock_result(
        tax_data_from_transactions,
        tax_data_from_dividends,
        num_transactions=len(transactions),
        num_files=len(filepaths),
    )


if __name__ == "__main__":
    stocks()
