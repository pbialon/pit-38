from typing import Dict

import pendulum

from data_sources.revolut.stock.csv_parser import StockCsvParser
from data_sources.revolut.stock.operation import OperationType
from domain.stock.operations.custody_fee import CustodyFee
from domain.stock.operations.dividend import Dividend
from domain.stock.operations.operation import Operation
from domain.stock.operations.stock_split import StockSplit


class OperationStockCsvParser(StockCsvParser):
    OPERATIONS_HANDLED = {
        OperationType.DIVIDEND,
        OperationType.CUSTODY_FEE,
        OperationType.STOCK_SPLIT
    }

    @classmethod
    def parse(cls, row: Dict) -> Operation:
        operation_type = cls._operation_type(row)
        if operation_type not in cls.OPERATIONS_HANDLED:
            return None
        if operation_type == OperationType.DIVIDEND:
            return OperationStockCsvParser._parse_dividend(row)
        if operation_type == OperationType.CUSTODY_FEE:
            return OperationStockCsvParser._parse_custody_fee(row)
        if operation_type == OperationType.STOCK_SPLIT:
            return OperationStockCsvParser._parse_stock_split(row)

    @classmethod
    def _parse_custody_fee(cls, row: Dict) -> CustodyFee:
        return CustodyFee(
            date=cls._date(row),
            value=cls._fiat_value(row)
        )

    @classmethod
    def _parse_dividend(cls, row: Dict) -> Dividend:
        return Dividend(
            date=cls._date(row),
            value=cls._fiat_value(row)
        )

    @classmethod
    def _parse_stock_split(cls, row: Dict) -> StockSplit:
        date = cls._date(row)
        stock = cls._stock(row)
        return StockSplit(
            date=date,
            stock=stock,
            ratio=cls._ratio(date, stock)
        )

    @classmethod
    def _ratio(cls, date: pendulum.Date, stock: str) -> int:
        split_ratio = input(f"Enter split ratio for stock {stock} on {date.to_date_string()} "
                            f"(e.g. if 20 shares for 1 - 20:1 - then type 20):")
        return int(split_ratio)
