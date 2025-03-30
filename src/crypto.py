from typing import List

import click

from data_sources.crypto_loader.csv_loader import Loader
from data_sources.crypto_loader.multi_sources_loader import MultiSourcesLoader
from domain.calendar_service.calendar import previous_year
from domain.crypto.profit_calculator import YearlyProfitCalculator
from domain.tax_service.tax_calculator import TaxCalculator
from domain.transactions import Transaction
from exchanger import create_exchanger
from loguru import logger
import sys


class CryptoSetup:
    @classmethod
    def setup_yearly_profit_calculator(cls) -> YearlyProfitCalculator:
        exchanger = create_exchanger()
        return YearlyProfitCalculator(exchanger)

    @classmethod
    def read_transactions(cls, filepaths: List[str]) -> List[Transaction]:
        transaction_loader = MultiSourcesLoader(Loader())
        return transaction_loader.load(filepaths)
    
    @classmethod
    def set_log_level(cls, log_level: str):
        logger.remove()
        logger.add(sys.stderr, level=log_level.upper())


@click.command()
@click.option('--tax-year', '-y', default=previous_year(), help='Year you want to calculate tax for')
@click.option('--filepaths', '-f', multiple=True, required=True,
              help='Paths to csv files with transactions')
@click.option('--deductible-loss', '-l', default=-1,
              help='Deductible loss from previous years. It overrides calculation of loss by the script',
              type=float)
@click.option('--log-level', '-ll', default='DEBUG', help='Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
def crypto(tax_year: int, filepaths: tuple[str, ...], deductible_loss: float, log_level: str):
    CryptoSetup.set_log_level(log_level)

    profit_calculator = CryptoSetup.setup_yearly_profit_calculator()
    all_transactions = CryptoSetup.read_transactions(list(filepaths))
    
    profit_per_year = profit_calculator.profit_per_year(all_transactions)
    tax_calculator = TaxCalculator()
    tax_data = tax_calculator.calculate_tax_per_year(profit_per_year, tax_year, deductible_loss)
    print(tax_data, end='\n\n')


if __name__ == "__main__":
    crypto()
