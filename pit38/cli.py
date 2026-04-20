import sys

import click
from loguru import logger

from pit38.stock import stocks
from pit38.crypto import crypto


def setup_logger(log_level: str):
    logger.remove()
    logger.add(sys.stderr, level=log_level)


@click.group()
def main():
    """PIT-38 — Polish investment tax calculator for stocks and cryptocurrency."""
    pass


@click.group()
def import_cmd():
    """Import broker exports into standardized CSV format."""
    pass


@import_cmd.command("revolut-stock")
@click.option("-i", "--input", "input_path", type=click.Path(exists=True), required=True, help="Revolut stock export CSV")
@click.option("-o", "--output", "output_path", type=click.Path(), required=True, help="Output standardized CSV")
@click.option("-ll", "--log-level", default="INFO", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]))
def import_revolut_stock(input_path, output_path, log_level):
    """Import stock transactions from Revolut."""
    setup_logger(log_level)
    from pit38.plugins.stock.revolut.csv import CsvService
    from pit38.plugins.stock.revolut.transaction_row_parser import TransactionRowParser
    from pit38.plugins.stock.revolut.operation_row_parser import OperationRowParser
    from pit38.plugins.stock.generic_saver import GenericCsvSaver

    transactions = CsvService(input_path, TransactionRowParser).read()
    operations = CsvService(input_path, OperationRowParser).read()
    GenericCsvSaver.save(transactions, operations, output_path)
    click.echo(f"Saved {len(transactions)} transactions and {len(operations)} operations to {output_path}")


@import_cmd.command("revolut-crypto")
@click.option("-i", "--input", "input_path", type=click.Path(exists=True), required=True, help="Revolut crypto export CSV")
@click.option("-o", "--output", "output_path", type=click.Path(), required=True, help="Output standardized CSV")
@click.option("-ll", "--log-level", default="INFO", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]))
def import_revolut_crypto(input_path, output_path, log_level):
    """Import crypto transactions from Revolut."""
    setup_logger(log_level)
    from pit38.plugins.crypto.revolut.csv import CsvService
    from pit38.plugins.crypto.revolut.row_parser import RowParser
    from pit38.plugins.crypto.generic_saver import GenericCsvSaver

    transactions = CsvService(RowParser()).read(input_path)
    GenericCsvSaver.save(transactions, output_path)
    click.echo(f"Saved {len(transactions)} transactions to {output_path}")


@import_cmd.command("etrade")
@click.option("-i", "--input", "input_path", type=click.Path(exists=True), required=True, help="E*Trade export CSV")
@click.option("-o", "--output", "output_path", type=click.Path(), required=True, help="Output standardized CSV")
@click.option("-ll", "--log-level", default="INFO", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]))
def import_etrade(input_path, output_path, log_level):
    """Import stock transactions from E*Trade."""
    setup_logger(log_level)
    from pit38.plugins.stock.etrade.csv import EtradeCsvReader
    from pit38.plugins.stock.generic_saver import GenericCsvSaver

    transactions = EtradeCsvReader.read(input_path)
    GenericCsvSaver.save(transactions, [], output_path)
    click.echo(f"Saved {len(transactions)} transactions to {output_path}")


@import_cmd.command("binance")
@click.option("-i", "--input", "input_path", type=click.Path(exists=True), required=True, help="Binance export CSV")
@click.option("-o", "--output", "output_path", type=click.Path(), required=True, help="Output standardized CSV")
@click.option("-ll", "--log-level", default="INFO", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]))
def import_binance(input_path, output_path, log_level):
    """Import crypto transactions from Binance."""
    setup_logger(log_level)
    from pit38.plugins.crypto.binance.csv import BinanceTransactionProcessor
    from pit38.plugins.crypto.generic_saver import GenericCsvSaver

    transactions = BinanceTransactionProcessor().read(input_path)
    GenericCsvSaver.save(transactions, output_path)
    click.echo(f"Saved {len(transactions)} transactions to {output_path}")


main.add_command(stocks, name="stock")
main.add_command(crypto, name="crypto")
main.add_command(import_cmd, name="import")


if __name__ == "__main__":
    main()
