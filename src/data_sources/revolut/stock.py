import enum
from typing import Dict

from domain.transactions import Transaction


class OperationType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    CUSTODY_FEE = "CUSTODY FEE"


class CsvParser:
    OPERATIONS = {
        OperationType.BUY: "BUY - MARKET",
        OperationType.SELL: "SELL - MARKET",
        OperationType.DIVIDEND: "DIVIDEND",
        OperationType.CUSTODY_FEE: "CUSTODY FEE",
    }

    @classmethod
    def parse(cls, row: Dict) -> Transaction:
        operation_type = CsvParser.OPERATIONS[row['Type']]
        if operation_type == OperationType.BUY:
            return CsvParser._parse_buy(row)
        elif operation_type == OperationType.SELL:
            return CsvParser._parse_sell(row)
        elif operation_type == OperationType.DIVIDEND:
            return CsvParser._parse_dividend(row)
        elif operation_type == OperationType.CUSTODY_FEE:
            return CsvParser._parse_custody_fee(row)

        return None

    @classmethod
    def _parse_buy(cls, row: Dict) -> Transaction:
        pass

    @classmethod
    def _parse_sell(cls, row: Dict) -> Transaction:
        pass

    @classmethod
    def _parse_dividend(cls, row: Dict) -> Transaction:
        pass

    @classmethod
    def _parse_custody_fee(cls, row: Dict) -> Transaction:
        pass
