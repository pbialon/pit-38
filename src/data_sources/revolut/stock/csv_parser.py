from typing import Dict

import pendulum

from data_sources.revolut.csv_reader import CsvParser
from data_sources.revolut.stock.operation import OperationType
from domain.currency_exchange_service.currencies import FiatValue, CurrencyBuilder
from domain.transactions import Transaction


class StockCsvParser(CsvParser):
    OPERATIONS = {
        "BUY - MARKET": OperationType.BUY,
        "SELL - MARKET": OperationType.SELL,
        "DIVIDEND": OperationType.DIVIDEND,
        "CUSTODY FEE": OperationType.CUSTODY_FEE,
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
        if amount_row.startswith("-"):
            amount_row = amount_row[1:]
        amount_row = amount_row[1:].replace(",", "")
        amount = float(amount_row)
        return FiatValue(amount, currency)

    @classmethod
    def _stock(cls, row: Dict) -> str:
        return row['Ticker']

    @classmethod
    def _date(cls, row: dict) -> pendulum.Date:
        return pendulum.parse(row['Date']).date()

    @classmethod
    def _operation_type(cls, row: dict) -> OperationType:
        return cls.OPERATIONS.get(row['Type'])
