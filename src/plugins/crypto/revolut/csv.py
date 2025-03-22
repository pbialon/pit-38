from typing import List
from loguru import logger
import csv  

from domain.transactions.transaction import Transaction
from plugins.crypto.revolut.row_parser import RowParser


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

    def save(self, transactions: List[Transaction], output_path: str):
        with open(output_path, 'w') as csvfile:
            # todo: move it to domain or data_sources
            writer = csv.DictWriter(csvfile, fieldnames=["date", "operation", "amount", "symbol", "fiat_value", "currency"])
            writer.writeheader()
            for transaction in transactions:
                writer.writerow({
                    "date": transaction.date.to_datetime_string(),
                    "operation": transaction.action,
                    "amount": f"{float(transaction.asset.amount):.8f}",
                    "symbol": transaction.asset.asset_name,
                    "fiat_value": f"{float(transaction.fiat_value.amount):.2f}",
                    "currency": transaction.fiat_value.currency
                })
