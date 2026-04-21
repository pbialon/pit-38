from typing import Dict

import pendulum

from pit38.domain.stock.operations.dividend import Dividend
from pit38.domain.stock.operations.operation import Operation
from pit38.domain.stock.operations.service_fee import ServiceFee
from pit38.domain.stock.operations.stock_market_operation import StockMarketOperation
from pit38.domain.stock.operations.stock_split import StockSplit
from pit38.plugins.stock.revolut.row_parser import RowParser


class OperationRowParser(RowParser):
    OPERATIONS_HANDLED = {
        StockMarketOperation.DIVIDEND,
        StockMarketOperation.SERVICE_FEE,
        StockMarketOperation.STOCK_SPLIT,
    }

    @classmethod
    def parse(cls, row: Dict) -> Operation:
        operation_type = cls._operation_type(row)
        if operation_type not in cls.OPERATIONS_HANDLED:
            return None
        if operation_type == StockMarketOperation.DIVIDEND:
            return cls._parse_dividend(row)
        if operation_type == StockMarketOperation.SERVICE_FEE:
            return cls._parse_service_fee(row)
        if operation_type == StockMarketOperation.STOCK_SPLIT:
            return cls._parse_stock_split(row)

    @classmethod
    def _parse_service_fee(cls, row: Dict) -> ServiceFee:
        return ServiceFee(
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