import re
from typing import Dict

import pendulum

from pit38.domain.currency_exchange_service.currencies import FiatValue, CurrencyBuilder
from pit38.domain.transactions import Transaction
from pit38.domain.stock.operations.operation import OperationType


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
        raw = row['Total Amount']
        if raw.startswith("-"):
            raw = raw[1:]

        # "USD 1317.06" or "EUR 500.00" — currency code + space + amount
        code_match = re.match(r'([A-Z]{3})\s+([\d,.]+)', raw)
        if code_match:
            currency = CurrencyBuilder.build(code_match.group(1))
            amount = float(code_match.group(2).replace(",", ""))
            return FiatValue(amount, currency)

        # "$1,003.01" or "€500.00" — currency symbol + amount
        symbol_match = re.match(r'([^\d\s])([\d,.]+)', raw)
        if symbol_match:
            currency = CurrencyBuilder.build(symbol_match.group(1))
            amount = float(symbol_match.group(2).replace(",", ""))
            return FiatValue(amount, currency)

        raise ValueError(f"Cannot parse Total Amount: '{row['Total Amount']}')")

    @classmethod
    def _stock(cls, row: Dict) -> str:
        return row['Ticker']

    @classmethod
    def _date(cls, row: dict) -> pendulum.DateTime:
        return pendulum.parse(row['Date'])

    @classmethod
    def _operation_type(cls, row: dict) -> OperationType:
        return cls.OPERATIONS.get(row['Type'])
