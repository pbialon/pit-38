from typing import Dict

from loguru import logger

from data_sources.revolut.stock.csv_parser import StockCsvParser
from data_sources.revolut.stock.operation import OperationType
from domain.transactions import Transaction, AssetValue


class TransactionStockCsvParser(StockCsvParser):
    OPERATIONS_HANDLED = {
        OperationType.BUY,
        OperationType.SELL,
    }

    @classmethod
    def parse(cls, row: Dict) -> Transaction:
        operation_type = cls._operation_type(row)
        if operation_type not in cls.OPERATIONS_HANDLED:
            return None

        transaction = TransactionStockCsvParser._parse_transaction(row)
        logger.debug(f"Parsed transaction: {transaction}")
        return transaction

    @classmethod
    def _parse_transaction(cls, row: Dict) -> Transaction:
        return Transaction(
            asset=cls._asset(row),
            fiat_value=cls._fiat_value(row),
            action=cls._operation_type(row),
            date=cls._date(row),
        )

    @classmethod
    def _asset(cls, row: Dict) -> AssetValue:
        return AssetValue(cls._quantity(row), cls._stock(row))

    @classmethod
    def _quantity(cls, row: Dict) -> float:
        return float(row['Quantity'])
