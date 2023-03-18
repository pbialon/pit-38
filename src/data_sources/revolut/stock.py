import enum
from typing import Dict

import pendulum
from loguru import logger

from domain.currency_exchange_service.currencies import CurrencyBuilder, FiatValue
from domain.stock.custody_fee import CustodyFee
from domain.stock.dividend import Dividend
from domain.transactions import Transaction, AssetValue


class OperationType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    CUSTODY_FEE = "CUSTODY FEE"


class StockCsvParser:
    OPERATIONS = {
        "BUY - MARKET": OperationType.BUY,
        "SELL - MARKET": OperationType.SELL,
        "DIVIDEND": OperationType.DIVIDEND,
        "CUSTODY FEE": OperationType.CUSTODY_FEE,
    }

    @classmethod
    def parse(cls, row: Dict) -> Transaction:
        operation_type = cls._operation_type(row)
        if operation_type in (OperationType.BUY, OperationType.SELL):
            return StockCsvParser._parse_transaction(row)
        elif operation_type == OperationType.DIVIDEND:
            return StockCsvParser._parse_dividend(row)
        elif operation_type == OperationType.CUSTODY_FEE:
            return StockCsvParser._parse_custody_fee(row)

        logger.debug(f"Skipping transaction: {row} (not supported)")
        return None

    @classmethod
    def _parse_transaction(cls, row: Dict) -> Transaction:
        return Transaction(
            asset=cls._asset(row),
            fiat_value=cls._fiat_value(row),
            action=cls._operation_type(row),
            date=cls._date(row),
        )

    @classmethod
    def _parse_dividend(cls, row: Dict) -> Transaction:
        return Dividend(
            date=cls._date(row),
            value=cls._fiat_value(row)
        )

    @classmethod
    def _parse_custody_fee(cls, row: Dict) -> Transaction:
        return CustodyFee(
            date=cls._date(row),
            value=cls._fiat_value(row)
        )

    @classmethod
    def _asset(cls, row: Dict) -> AssetValue:
        return AssetValue(cls._stock(row), cls._quantity(row))

    @classmethod
    def _stock(cls, row: Dict) -> str:
        return row['Ticker']

    @classmethod
    def _quantity(cls, row: Dict) -> float:
        return float(row['Quantity'])

    @classmethod
    def _fiat_value(cls, row: Dict) -> FiatValue:
        currency = CurrencyBuilder.build(row['Currency'])
        amount_row = row['Total Amount']
        # e.g. amount_row == "-$1,003.01"
        if amount_row.startswith("-"):
            amount_row = amount_row[1:]
        amount_row = amount_row[1:].replace(",", "")
        amount = float(amount_row)
        return FiatValue(amount, currency)

    @classmethod
    def _date(cls, row: dict) -> pendulum.DateTime:
        return pendulum.parse(row['Date'])

    @classmethod
    def _operation_type(cls, row: dict) -> OperationType:
        return cls.OPERATIONS.get(row['Type'])
