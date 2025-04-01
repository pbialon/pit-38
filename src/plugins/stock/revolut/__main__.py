import os
import sys
import click
from loguru import logger

from plugins.stock.revolut.operation_row_parser import OperationRowParser
from plugins.stock.revolut.csv import CsvService
from plugins.stock.revolut.transaction_row_parser import TransactionRowParser
from plugins.stock.generic_saver import GenericCsvSaver

def setup_logger(log_level: str):
    logger.remove()
    logger.add(sys.stderr, level=log_level)


@click.command()
@click.option('--input-path', type=click.Path(exists=True), required=True)
@click.option('--output-path', type=click.Path(), required=True)
@click.option('--log-level', type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]), default='INFO')
def main(input_path, output_path, log_level):
    setup_logger(log_level)

    transactions_reader = CsvService(input_path, TransactionRowParser)
    operations_reader = CsvService(input_path, OperationRowParser)

    transactions = transactions_reader.read()
    operations = operations_reader.read()

    GenericCsvSaver.save(transactions, operations, output_path)
    logger.info(f"Saved {len(transactions)} transactions and {len(operations)} operations to {output_path}")


if __name__ == "__main__":
    main()
