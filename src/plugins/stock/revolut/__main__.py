import os
import sys
import click
from loguru import logger

from plugins.stock.revolut.operation_csv_parser import OperationStockCsvParser
from plugins.stock.revolut.operations_csv_reader import OperationsCsvReader
from plugins.stock.revolut.transaction_csv_parser import TransactionStockCsvParser
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

    transactions_reader = OperationsCsvReader(input_path, TransactionStockCsvParser)
    operations_reader = OperationsCsvReader(input_path, OperationStockCsvParser)

    transactions = transactions_reader.read()
    operations = operations_reader.read()

    GenericCsvSaver.save(transactions, operations, output_path)
    logger.info(f"Saved {len(transactions)} transactions and {len(operations)} operations to {output_path}")


if __name__ == "__main__":
    main()
