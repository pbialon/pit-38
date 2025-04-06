from abc import ABC, abstractmethod
from typing import Dict, Any, Type
from domain.transactions import Transaction
from domain.stock.operations.stock_split import StockSplit
from domain.stock.operations.custody_fee import CustodyFee
from domain.stock.operations.dividend import Dividend


class BaseFormatter(ABC):
    @abstractmethod
    def format(self, item: Any) -> Dict[str, Any]:
        pass

    @abstractmethod
    def item_type(self) -> Type:
        pass


class TransactionFormatter(BaseFormatter):
    def format(self, transaction: Transaction) -> Dict[str, Any]:
        return {
            "date": transaction.date.to_datetime_string(),
            "operation": transaction.action,
            "amount": f"{float(transaction.asset.amount):.8f}",
            "symbol": transaction.asset.asset_name,
            "fiat_value": f"{float(transaction.fiat_value.amount):.2f}",
            "currency": transaction.fiat_value.currency
        }

    def item_type(self) -> Type:
        return Transaction


class StockSplitFormatter(BaseFormatter):
    OPERATION = "STOCK_SPLIT"

    def format(self, operation: StockSplit) -> Dict[str, Any]:
        return {
            "date": operation.date.to_datetime_string(),
            "operation": self.OPERATION,
            "amount": operation.ratio,
            "symbol": operation.stock,
            "fiat_value": "",
            "currency": ""
        }

    def item_type(self) -> Type:
        return StockSplit


class CustodyFeeFormatter(BaseFormatter):
    OPERATION = "SERVICE_FEE"

    def format(self, operation: CustodyFee) -> Dict[str, Any]:
        return {
            "date": operation.date.to_datetime_string(),
            "operation": self.OPERATION,
            "amount": "",
            "symbol": "",
            "fiat_value": f"{operation.value.amount:.2f}",
            "currency": operation.value.currency
        }

    def item_type(self) -> Type:
        return CustodyFee


class DividendFormatter(BaseFormatter):
    OPERATION = "DIVIDEND"

    def format(self, operation: Dividend) -> Dict[str, Any]:
        return {
            "date": operation.date.to_datetime_string(),
            "operation": self.OPERATION,
            "amount": "",
            "symbol": "",
            "fiat_value": f"{operation.value.amount:.2f}",
            "currency": operation.value.currency
        }

    def item_type(self) -> Type:
        return Dividend