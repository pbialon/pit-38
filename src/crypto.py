from typing import List

import click

from data_sources.revolut.crypto import CryptoCsvParser
from data_sources.revolut.csv_reader import TransactionsCsvReader
from domain.calendar_service.calendar import previous_year
from domain.crypto.profit_calculator import YearlyProfitCalculator
from domain.crypto.tax import TaxCalculator
from domain.transactions import Transaction
from exchanger import create_exchanger


class CryptoSetup:
    @classmethod
    def setup_tax_calculator(cls) -> TaxCalculator:
        exchanger = create_exchanger()
        profit_calculator = YearlyProfitCalculator(exchanger)
        return TaxCalculator(profit_calculator)

    @classmethod
    def read_transactions(cls, filepath: str) -> List[Transaction]:
        return TransactionsCsvReader(filepath, CryptoCsvParser).read()


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


if __name__ == "__main__":
    crypto()
