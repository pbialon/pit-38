from typing import List

import click

from data_sources.revolut.crypto import CryptoCsvParser
from data_sources.revolut.csv_reader import TransactionsCsvReader
from domain.calendar_service.calendar import previous_year
from domain.crypto.profit_calculator import YearlyProfitCalculator
from domain.tax_service.tax_calculator import TaxCalculator
from domain.transactions import Transaction
from exchanger import create_exchanger


class CryptoSetup:
    @classmethod
    def setup_yearly_profit_calculator(cls) -> YearlyProfitCalculator:
        exchanger = create_exchanger()
        return YearlyProfitCalculator(exchanger)

    @classmethod
    def read_transactions(cls, filepath: str) -> List[Transaction]:
        return TransactionsCsvReader(filepath, CryptoCsvParser).read()


@click.command()
@click.option('--tax-year', '-y', default=previous_year(), help='Year you want to calculate tax for')
@click.option('--filepath', '-f',
              help='Path to csv file with transactions (currently only revolut csv format is supported)')
@click.option('--deductible-loss', '-l', default=-1,
              help='Deductible loss from previous years. It overrides calculation of loss by the script',
              type=float)
def crypto(tax_year: int, filepath: str, deductible_loss: float):
    profit_calculator = CryptoSetup.setup_yearly_profit_calculator()
    transactions = CryptoSetup.read_transactions(filepath)
    cost_per_year = profit_calculator.cost_per_year(transactions)
    income_per_year = profit_calculator.income_per_year(transactions)
    tax_calculator = TaxCalculator()
    tax_data = tax_calculator.calculate_tax_per_year(
        income_per_year, cost_per_year, tax_year, deductible_loss)
    print(tax_data, end='\n\n')


if __name__ == "__main__":
    crypto()
