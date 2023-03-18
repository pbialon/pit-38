from typing import List
import pendulum
import click

from data_sources.revolut.crypto import CryptoCsvParser
from data_sources.revolut.csv_reader import TransactionsCsvReader
from domain.calendar_service.calendar import Calendar, year_start, year_end, previous_year
from domain.crypto.profit_calculator import YearlyProfitCalculator
from domain.crypto.tax import TaxCalculator
from domain.transactions import Transaction
from domain.currency_exchange_service.exchange_rates_provider import ExchangeRatesProvider
from domain.currency_exchange_service.exchanger import Exchanger


def create_exchanger(start_date: pendulum.Date, end_date: pendulum.Date) -> Exchanger:
    calendar = Calendar()
    rates_provider = ExchangeRatesProvider(start_date, end_date)
    return Exchanger(rates_provider, calendar)


class CryptoSetup:
    def __init__(self, start_date: pendulum.Date, end_date: pendulum.Date):
        self.start_date = start_date
        self.end_date = end_date

    def setup_tax_calculator(self) -> TaxCalculator:
        exchanger = create_exchanger(self.start_date, self.end_date)
        profit_calculator = YearlyProfitCalculator(exchanger)
        return TaxCalculator(profit_calculator)

    def read_transactions(self, filepath: str) -> List[Transaction]:
        return TransactionsCsvReader(filepath, CryptoCsvParser).read()


@click.command()
@click.option('--tax-year', '-y', default=previous_year(), help='Year you want to calculate tax for')
@click.option('--filepath', '-f',
              help='Path to csv file with transactions (currently only revolut csv format is supported)')
@click.option('--deductable-loss', '-l', default=-1,
              help='Deductable loss from previous years. It overrides calculation of loss by the script',
              type=float)
def crypto(tax_year: int, filepath: str, deductable_loss: int):
    crypto_setup = CryptoSetup(year_start(tax_year), year_end(tax_year))
    tax_calculator = crypto_setup.setup_tax_calculator()
    transactions = crypto_setup.read_transactions(filepath)
    tax_data = tax_calculator.calculate_tax_per_year(transactions, tax_year, deductable_loss)
    print(tax_data, end='\n\n')


@click.command()
@click.option('--tax-year', '-y', default=previous_year(), help='Year you want to calculate tax for')
@click.option('--filepath', '-f',
              help='Path to csv file with transactions (currently only revolut csv format is supported)')
def stocks(tax_year: int, filepath: str):
    pass


if __name__ == "__main__":
    crypto()
