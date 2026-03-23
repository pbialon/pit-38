from typing import Dict

import pendulum

from domain.currency_exchange_service.currencies import FiatValue, CurrencyBuilder
from domain.transactions import Transaction
from domain.stock.operations.operation import OperationType


class RowParser:
    OPERATIONS = {
        "BUY": OperationType.BUY,
        "SELL": OperationType.SELL,
        "DIVIDEND": OperationType.DIVIDEND,
        "CUSTODY FEE": OperationType.SERVICE_FEE,
        "STOCK SPLIT": OperationType.STOCK_SPLIT,
    }

    @classmethod
    def parse(cls, row: Dict) -> Transaction:
        raise NotImplementedError

    @classmethod
    def _fiat_value(cls, row: Dict) -> FiatValue:
        currency = CurrencyBuilder.build(row['Currency'])
        # e.g."-$1,003.01"
        amount_row = row['Total Amount']
        amount_row = amount_row.strip(str(currency))
        if amount_row.startswith("-"):
            amount_row = amount_row[1:]
        amount_row = amount_row[1:].replace(",", "")
        amount = float(amount_row)
        return FiatValue(amount, currency)

    @classmethod
    def _stock(cls, row: Dict) -> str:
        return row['Ticker']

    @classmethod
    def _date(cls, row: dict) -> pendulum.DateTime:
        return pendulum.parse(row['Date'])

    @classmethod
    def _operation_type(cls, row: dict) -> OperationType:
        operation_type = cls.OPERATIONS.get(row['Type'])
        if operation_type:
            return operation_type
        for operation_name, operation_type in cls.OPERATIONS.items():
            if operation_name in row['Type']:
                return operation_type
        return None
