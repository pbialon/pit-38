import sys
from collections import Counter

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


def _print_skipped_summary(skipped_by_type: Counter) -> None:
    """Pretty-print a skip summary to stderr for the user to review."""
    if not skipped_by_type:
        return
    total = sum(skipped_by_type.values())
    click.echo(
        f"\nSkipped {total} rows (operation types not recognized as tax-relevant):",
        err=True,
    )
    for op_type, count in skipped_by_type.most_common():
        click.echo(f"  • {op_type}: {count} rows", err=True)
    click.echo(
        "\nIf you believe any of these should be taxed, please check with your\n"
        "tax advisor and open an issue: https://github.com/pbialon/pit-38/issues",
        err=True,
    )


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

    # Both parsers scan every row; they skip the same unknown-type rows, so
    # the skip counters are identical. Report just once (from the first pass).
    transaction_result = CsvService(input_path, TransactionRowParser).read_with_summary()
    operation_result = CsvService(input_path, OperationRowParser).read_with_summary()

    GenericCsvSaver.save(transaction_result.records, operation_result.records, output_path)
    click.echo(
        f"Saved {len(transaction_result.records)} transactions and "
        f"{len(operation_result.records)} operations to {output_path}"
    )
    _print_skipped_summary(transaction_result.skipped_by_type)


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


@import_cmd.command("ibi-capital")
@click.option("-i", "--input", "input_paths", type=click.Path(exists=True),
              multiple=True, required=True,
              help="IBI order confirmation PDF or directory of PDFs (repeatable)")
@click.option("-o", "--output", "output_path", type=click.Path(), required=True, help="Output standardized CSV")
@click.option("--ticker", default=None,
              help="Override ticker (skips companies.json lookup — useful for companies not yet in the seed)")
@click.option("-ll", "--log-level", default="INFO", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]))
def import_ibi_capital(input_paths, output_path, ticker, log_level):
    """Import stock sale confirmations from IBI Capital (Israeli broker, PDF input)."""
    setup_logger(log_level)

    from pathlib import Path
    from pit38.plugins.stock.generic_saver import GenericCsvSaver
    from pit38.plugins.stock.ibi_capital.company_ticker import resolve_ticker
    from pit38.plugins.stock.ibi_capital.order_parser import parse_order_report
    from pit38.plugins.stock.ibi_capital.pdf_reader import extract_text
    from pit38.plugins.stock.ibi_capital.record_builder import build_records

    pdfs: list[Path] = []
    for raw in input_paths:
        p = Path(raw)
        pdfs.extend(sorted(p.rglob("*.pdf")) if p.is_dir() else [p])

    if not pdfs:
        click.echo("No PDF files found under the provided --input paths.", err=True)
        raise click.Abort()

    transactions = []
    fees = []
    for pdf_path in pdfs:
        parsed = parse_order_report(extract_text(pdf_path))
        resolved = resolve_ticker(parsed.company, override=ticker)
        t, f = build_records(parsed, resolved)
        transactions.extend(t)
        fees.extend(f)

    GenericCsvSaver.save(transactions, fees, output_path)
    click.echo(
        f"Saved {len(transactions)} transactions and {len(fees)} service fees "
        f"from {len(pdfs)} IBI Capital PDF(s) to {output_path}"
    )


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
