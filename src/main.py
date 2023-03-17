from typing import List
import pendulum
import click

from data_sources.revolut.crypto import CsvReader, CsvParser
from domain.calendar_service.calendar import Calendar
from domain.crypto.profit_calculator import YearlyProfitCalculator
from domain.crypto.tax import TaxCalculator
from domain.transactions import Transaction
from domain.currency_exchange_service.exchange_rates_provider import ExchangeRatesProvider
from domain.currency_exchange_service.exchanger import Exchanger


def setup_tax_calculator(start_date: pendulum.Date, end_date: pendulum.Date) -> TaxCalculator:
    calendar = Calendar()
    rates_provider = ExchangeRatesProvider(start_date, end_date)
    exchanger = Exchanger(rates_provider, calendar)
    profit_calculator = YearlyProfitCalculator(exchanger)
    return TaxCalculator(profit_calculator)


def setup_input_data(filepath: str) -> List[Transaction]:
    return CsvReader(filepath, CsvParser).read()


def crypto(tax_year: int, transactions_data_filepath: str, deductable_loss: int):
    tax_year_start = pendulum.date(tax_year, 1, 1)
    tax_year_end = pendulum.date(tax_year, 12, 31)
    tax_calculator = setup_tax_calculator(tax_year_start, tax_year_end)
    transactions = setup_input_data(transactions_data_filepath)
    tax_data = tax_calculator.calculate_tax_per_year(transactions, tax_year, deductable_loss)
    print(tax_data, end='\n\n')


def previous_year():
    return pendulum.now().year - 1


@click.command()
@click.option('--filepath', '-f', help='Path to csv file with transactions')
@click.option('--tax-year', '-y', default=previous_year(), help='Year you want to calculate tax for')
@click.option('--deductable-loss', '-l', default=-1,
              help='Deductable loss from previous years. It overrides calculation of loss by the script',
              type=float)
def main(filepath, tax_year, deductable_loss):
    # TODO: add other options than just revolut file
    crypto(tax_year, filepath, deductable_loss)


if __name__ == "__main__":
    main()
