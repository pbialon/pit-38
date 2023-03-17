import csv
from typing import List

from loguru import logger

from domain.transactions import Transaction


class CsvParser:
    @staticmethod
    def parse(row):
        raise NotImplementedError


class TransactionsCsvReader:
    def __init__(self, path: str, csv_parser: CsvParser):
        self.path = path
        self.csv_parser = csv_parser

    def read(self) -> List[Transaction]:
        transactions = []
        logger.info(f"Reading transactions from {self.path}...")
        with open(self.path, 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for row in reader:
                transaction = self.csv_parser.parse(row)
                if not transaction:
                    continue

                transactions.append(transaction)
        logger.info(f"Parsed {len(transactions)} transactions")
        return transactions
