from typing import Dict

import pendulum

from domain.currency_exchange_service.currencies import FiatValue, CurrencyBuilder
from domain.transactions import Transaction
from domain.stock.operations.operation import OperationType


class RowParser:
    OPERATIONS = {
        "BUY - MARKET": OperationType.BUY,
        "BUY - LIMIT": OperationType.BUY,
        "SELL - MARKET": OperationType.SELL,
        "SELL - LIMIT": OperationType.SELL,
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
        # e.g. "-$1,003.01" or "USD 7992"
        amount_row = row['Total Amount']
        if amount_row.startswith("-"):
            amount_row = amount_row[1:]
        # Handle "USD 7992" format (currency code + space + amount)
        if " " in amount_row:
            amount_row = amount_row.split(" ", 1)[1]
        # Handle "$1,003.01" format (currency symbol prefix)
        elif amount_row and not amount_row[0].isdigit():
            amount_row = amount_row[1:]
        amount_row = amount_row.replace(",", "")
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
        return cls.OPERATIONS.get(row['Type'])
