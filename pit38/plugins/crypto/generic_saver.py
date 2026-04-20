import csv
from typing import List
from pit38.domain.transactions import Transaction


class GenericCsvSaver:
    @staticmethod
    def save(transactions: List[Transaction], file_path: str):
        with open(file_path, 'w') as csvfile:
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
