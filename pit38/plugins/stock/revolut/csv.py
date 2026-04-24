from collections import Counter
from dataclasses import dataclass, field
from typing import List

from loguru import logger

from pit38.data_sources.csv_utils import open_csv_reader
from pit38.domain.stock.operations.operation import Operation
from pit38.domain.transactions.transaction import Transaction
from pit38.plugins.stock.revolut.row_parser import RowParser


@dataclass
class ReadResult:
    """Result of reading a broker CSV: parsed records plus a summary of
    rows we intentionally skipped (unknown operation types, empty rows)."""
    records: List[Operation | Transaction]
    skipped_by_type: Counter = field(default_factory=Counter)

    @property
    def total_skipped(self) -> int:
        return sum(self.skipped_by_type.values())


class CsvService:
    def __init__(self, path: str, row_parser: RowParser):
        self.path = path
        self.row_parser = row_parser

    def read(self) -> List[Operation | Transaction]:
        """Backward-compatible: return only the records list.

        For the full result with skip summary, use read_with_summary().
        """
        return self.read_with_summary().records

    def read_with_summary(self) -> ReadResult:
        records: List[Operation | Transaction] = []
        skipped: Counter = Counter()
        logger.info(f"Reading records from {self.path}...")

        with open_csv_reader(self.path) as reader:
            for row in reader:
                op_type = self.row_parser._operation_type(row)
                if op_type is None:
                    raw_type = (row.get("type") or "").strip() or "<empty>"
                    skipped[raw_type] += 1
                    continue

                record = self.row_parser.parse(row)
                if record is None:
                    # Parser decided this specific row doesn't belong to its
                    # OPERATIONS_HANDLED set (e.g. TransactionRowParser sees
                    # a DIVIDEND row). Not an error — different parser will
                    # pick it up on another pass.
                    continue
                records.append(record)

        logger.info(f"Parsed {len(records)} records ({sum(skipped.values())} rows skipped)")
        return ReadResult(records=records, skipped_by_type=skipped)
