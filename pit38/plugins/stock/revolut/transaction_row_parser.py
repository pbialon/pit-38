from typing import Dict

from loguru import logger

from pit38.domain.stock.operations.stock_market_operation import StockMarketOperation
from pit38.domain.transactions import Transaction, AssetValue
from pit38.plugins.stock.revolut.row_parser import RowParser


class TransactionRowParser(RowParser):
    OPERATIONS_HANDLED = {
        StockMarketOperation.BUY,
        StockMarketOperation.SELL,
    }

    @classmethod
    def parse(cls, row: Dict) -> Transaction:
        operation_type = cls._operation_type(row)
        if operation_type not in cls.OPERATIONS_HANDLED:
            return None

        transaction = cls._parse_transaction(row)
        logger.debug(f"Parsed transaction: {transaction}")
        return transaction

    @classmethod
    def _parse_transaction(cls, row: Dict) -> Transaction:
        return Transaction(
            asset=cls._asset(row),
            fiat_value=cls._fiat_value(row),
            action=cls._operation_type(row).to_action(),
            date=cls._date(row),
        )

    @classmethod
    def _asset(cls, row: Dict) -> AssetValue:
        return AssetValue(cls._quantity(row), cls._stock(row))

    @classmethod
    def _quantity(cls, row: Dict) -> float:
        return float(row['Quantity']) 