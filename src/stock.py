from typing import List
import click

from data_sources.revolut.csv_reader import TransactionsCsvReader
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


class StockSetup:

    @classmethod
    def setup_profit_calculator(cls) -> ProfitCalculator:
        exchanger = create_exchanger()
        per_stock_calculator = PerStockProfitCalculator(exchanger)
        return ProfitCalculator(exchanger, per_stock_calculator)

    @classmethod
    def read_transactions(cls, filepath: str) -> List:
        return TransactionsCsvReader(filepath, TransactionStockCsvParser).read()

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
@click.option('--filepath', '-f',
              help='Path to csv file with transactions (currently only revolut csv format is supported)')
@click.option('--deductible-loss', '-l', default=-1,
              help='Deductible loss from previous years. It overrides calculation of loss by the script',
              type=float)
def stocks(tax_year: int, filepath: str, deductible_loss: float):
    stock_setup = StockSetup()
    transactions = stock_setup.read_transactions(filepath)
    operations = stock_setup.read_operations(filepath)
    custody_fees = stock_setup.filter_custody_fees(operations)
    dividends = stock_setup.filter_dividends(operations)
    stock_splits = stock_setup.filter_stock_splits(operations)

    profit_calculator = stock_setup.setup_profit_calculator()
    profit = profit_calculator.calculate_cumulative_cost_and_income(
        transactions, stock_splits, dividends, custody_fees)

    tax_calculator = TaxCalculator()
    tax_data = tax_calculator.calculate_tax_per_year(
        profit.income, profit.cost, tax_year, deductible_loss)
    print(tax_data, end='\n\n')


if __name__ == "__main__":
    stocks()
