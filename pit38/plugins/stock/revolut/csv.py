import csv
from typing import List

from loguru import logger

from pit38.domain.stock.operations.operation import Operation
from pit38.domain.transactions.transaction import Transaction
from pit38.plugins.stock.revolut.row_parser import RowParser


class CsvService:
    def __init__(self, path: str, row_parser: RowParser):
        self.path = path
        self.row_parser = row_parser

    def read(self) -> List[Operation | Transaction]:
        records = []
        logger.info(f"Reading records from {self.path}...")
        with open(self.path, 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for row in reader:
                operation = self.row_parser.parse(row)
                if not operation:
                    continue

                records.append(operation)
        logger.info(f"Parsed {len(records)} records")
        return records 