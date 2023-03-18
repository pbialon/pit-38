from typing import List, Dict
import pendulum
import click

from data_sources.revolut.crypto import CryptoCsvParser
from data_sources.revolut.csv_reader import TransactionsCsvReader
from data_sources.revolut.stock import StockCsvParser
from domain.calendar_service.calendar import Calendar, previous_year, today
from domain.crypto.profit_calculator import YearlyProfitCalculator
from domain.crypto.tax import TaxCalculator
from domain.stock.profit_calculator import YearlyPerStockProfitCalculator, group_transaction_by_company
from domain.transactions import Transaction
from domain.currency_exchange_service.exchange_rates_provider import ExchangeRatesProvider
from domain.currency_exchange_service.exchanger import Exchanger

DISTANT_PAST = pendulum.Date(2015, 1, 1)


def create_exchanger() -> Exchanger:
    calendar = Calendar()
    rates_provider = ExchangeRatesProvider(DISTANT_PAST, today())
    return Exchanger(rates_provider, calendar)


class CryptoSetup:
    @classmethod
    def setup_tax_calculator(cls) -> TaxCalculator:
        exchanger = create_exchanger()
        profit_calculator = YearlyProfitCalculator(exchanger)
        return TaxCalculator(profit_calculator)

    @classmethod
    def read_transactions(cls, filepath: str) -> List[Transaction]:
        return TransactionsCsvReader(filepath, CryptoCsvParser).read()


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
@click.option('--deductable-loss', '-l', default=-1,
              help='Deductable loss from previous years. It overrides calculation of loss by the script',
              type=float)
def crypto(tax_year: int, filepath: str, deductable_loss: int):
    tax_calculator = CryptoSetup.setup_tax_calculator()
    transactions = CryptoSetup.read_transactions(filepath)
    tax_data = tax_calculator.calculate_tax_per_year(transactions, tax_year, deductable_loss)
    print(tax_data, end='\n\n')


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
        result = profit_calculator.calculate_profit(transactions)


if __name__ == "__main__":
    stocks()
