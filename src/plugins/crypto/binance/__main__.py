
import click
from loguru import logger
import sys

from plugins.crypto.binance.csv import BinanceTransactionProcessor
from plugins.crypto.generic_saver import GenericCsvSaver


def setup_logger(log_level: str):
    logger.remove()
    logger.add(sys.stderr, level=log_level)


@click.command()
@click.option("--input-path", type=click.Path(exists=True), required=True)
@click.option("--output-path", type=click.Path(exists=False), required=True)
@click.option("--log-level", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]), default="INFO")
def main(input_path: str, output_path: str, log_level: str):
    setup_logger(log_level)

    transactions = BinanceTransactionProcessor().read(input_path)
    GenericCsvSaver.save(transactions, output_path)

if __name__ == "__main__":
    main()
