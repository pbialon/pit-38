from typing import List
from loguru import logger
import csv  

from pit38.domain.transactions.transaction import Transaction
from pit38.plugins.crypto.revolut.row_parser import RowParser


class CsvService:
    def __init__(self, row_parser: RowParser):
        self.row_parser = row_parser

    def read(self, input_path: str) -> List[Transaction]:
        transactions = []
        logger.info(f"Reading transactions from {input_path}...")
        with open(input_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for row in reader:
                transaction = self.row_parser.parse(row)
                if not transaction:
                    continue
                transactions.append(transaction)

        logger.info(f"Parsed {len(transactions)} transactions")
        return transactions
