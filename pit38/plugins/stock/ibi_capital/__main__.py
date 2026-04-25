"""Standalone CLI entry: ``python -m pit38.plugins.stock.ibi_capital``.

Mirrors ``pit38/plugins/stock/revolut/__main__.py``. The user-facing CLI
lives in ``pit38/cli.py`` (``pit38 import ibi-capital``) and is the
supported path; this entry point is a convenience for plugin-level
debugging.
"""
from __future__ import annotations

import sys
from pathlib import Path

import click
from loguru import logger

from pit38.plugins.stock.generic_saver import GenericCsvSaver
from pit38.plugins.stock.ibi_capital.company_ticker import resolve_ticker
from pit38.plugins.stock.ibi_capital.order_parser import parse_order_report
from pit38.plugins.stock.ibi_capital.pdf_reader import extract_text
from pit38.plugins.stock.ibi_capital.record_builder import build_records


def setup_logger(log_level: str) -> None:
    logger.remove()
    logger.add(sys.stderr, level=log_level)


def _collect_pdfs(paths: tuple[str, ...]) -> list[Path]:
    """Expand file/directory inputs into a flat list of PDF paths."""
    resolved: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            resolved.extend(sorted(p.rglob("*.pdf")))
        else:
            resolved.append(p)
    return resolved


@click.command()
@click.option(
    "-i", "--input", "input_paths",
    type=click.Path(exists=True), multiple=True, required=True,
    help="IBI order confirmation PDF or directory of PDFs (repeatable)",
)
@click.option("-o", "--output", "output_path", type=click.Path(), required=True)
@click.option("--ticker", default=None, help="Override ticker (skips companies.json lookup)")
@click.option(
    "-ll", "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="INFO",
)
def main(input_paths, output_path, ticker, log_level):
    setup_logger(log_level)

    all_transactions = []
    all_fees = []
    for pdf_path in _collect_pdfs(input_paths):
        logger.debug(f"Reading {pdf_path}")
        parsed = parse_order_report(extract_text(pdf_path))
        resolved_ticker = resolve_ticker(parsed.company, override=ticker)
        transactions, fees = build_records(parsed, resolved_ticker)
        all_transactions.extend(transactions)
        all_fees.extend(fees)

    GenericCsvSaver.save(all_transactions, all_fees, output_path)
    click.echo(
        f"Saved {len(all_transactions)} transactions and {len(all_fees)} "
        f"service fees to {output_path}"
    )


if __name__ == "__main__":
    main()
