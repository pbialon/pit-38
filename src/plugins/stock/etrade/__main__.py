import click
from loguru import logger

from plugins.stock.etrade.csv import EtradeCsvReader
from plugins.stock.generic_saver import GenericCsvSaver

@click.command()
@click.option("--input-path", type=click.Path(exists=True))
@click.option("--output-path", type=click.Path())
def main(input_path: str, output_path: str):
    logger.info(f"Reading transactions from {input_path}")
    transactions = EtradeCsvReader.read(input_path)
    logger.info(f"Found {len(transactions)} transactions")
    GenericCsvSaver.save(transactions, output_path)
    return transactions


if __name__ == "__main__":
    main() 