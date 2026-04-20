import csv
from typing import List, Dict, Any
from pit38.domain.transactions import Transaction
from pit38.domain.stock.operations.stock_split import StockSplit
from pit38.domain.stock.operations.service_fee import ServiceFee
from pit38.domain.stock.operations.dividend import Dividend
from .formatters import (
    TransactionFormatter,
    StockSplitFormatter,
    ServiceFeeFormatter,
    DividendFormatter
)


class GenericCsvSaver:
    FORMATTERS = {
        formatter.item_type(): formatter
        for formatter in [
            TransactionFormatter(),
            StockSplitFormatter(),
            ServiceFeeFormatter(),
            DividendFormatter()
        ]
    }

    @staticmethod
    def _format_item(item: Transaction | StockSplit | ServiceFee | Dividend) -> Dict[str, Any]:
        formatter = GenericCsvSaver.FORMATTERS.get(type(item))
        if not formatter:
            raise ValueError(f"Unsupported item type: {type(item)}")
        return formatter.format(item)

    @staticmethod
    def _write_entries(entries: List[Dict[str, Any]], writer: csv.DictWriter) -> None:
        for entry in entries:
            writer.writerow(entry)

    @staticmethod
    def save(transactions: List[Transaction], operations: List[StockSplit | ServiceFee | Dividend], file_path: str):
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=["date", "operation", "amount", "symbol", "fiat_value", "currency"]
            )
            writer.writeheader()

            all_entries = (
                [GenericCsvSaver._format_item(t) for t in transactions] +
                [GenericCsvSaver._format_item(o) for o in operations]
            )

            all_entries.sort(key=lambda x: x["date"])
            GenericCsvSaver._write_entries(all_entries, writer)
