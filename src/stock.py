from typing import List, Dict
import click

from data_sources.revolut.csv_reader import TransactionsCsvReader
from data_sources.revolut.stock import StockCsvParser
from domain.calendar_service.calendar import previous_year
from domain.stock.profit_calculator import YearlyPerStockProfitCalculator, group_transaction_by_company
from domain.transactions import Transaction
from exchanger import create_exchanger


class StockSetup:

    @classmethod
    def setup_profit_calculator(cls) -> YearlyPerStockProfitCalculator:
        exchanger = create_exchanger()
        return YearlyPerStockProfitCalculator(exchanger)

    @classmethod
    def read_transactions(cls, filepath: str) -> List:
        return TransactionsCsvReader(filepath, StockCsvParser).read()

    @classmethod
    def group_transactions_by_stock(cls, transactions: List[Transaction]) -> Dict[str, List[Transaction]]:
        return group_transaction_by_company(transactions)


@click.command()
@click.option('--tax-year', '-y', default=previous_year(), help='Year you want to calculate tax for')
@click.option('--filepath', '-f',
              help='Path to csv file with transactions (currently only revolut csv format is supported)')
def stocks(tax_year: int, filepath: str):
    stock_setup = StockSetup()
    transactions = stock_setup.read_transactions(filepath)
    grouped_transactions = stock_setup.group_transactions_by_stock(transactions)
    for company, transactions in grouped_transactions.items():
        profit_calculator = stock_setup.setup_profit_calculator()
        profit_calculator.calculate_profit(transactions)


if __name__ == "__main__":
    stocks()
