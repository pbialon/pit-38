
import click
from plugins.crypto.revolut.csv import CsvService
from plugins.crypto.revolut.row_parser import RowParser
from loguru import logger
import sys


def setup_logger(log_level: str):
    logger.remove()
    logger.add(sys.stderr, level=log_level)


@click.command()
@click.option("--input-path", type=click.Path(exists=True), required=True)
@click.option("--output-path", type=click.Path(exists=False), required=True)
@click.option("--log-level", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]), default="INFO")
def main(input_path: str, output_path: str, log_level: str):
    setup_logger(log_level)

    row_parser = RowParser()
    csv_service = CsvService(row_parser)
    transactions = csv_service.read(input_path)
    csv_service.save(transactions, output_path)

if __name__ == "__main__":
    main()
