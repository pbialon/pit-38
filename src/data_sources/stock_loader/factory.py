import pendulum
from typing import Optional

from domain.stock.operations.operation import Operation, OperationType
from domain.stock.operations.custody_fee import CustodyFee
from domain.stock.operations.dividend import Dividend
from domain.stock.operations.stock_split import StockSplit
from domain.currency_exchange_service.currencies import FiatValue
from domain.transactions.action import Action
from domain.transactions.asset import AssetValue
from src.domain.transactions.transaction import Transaction

class OperationFactory:
    _creators = {
        OperationType.CUSTODY_FEE: lambda date, asset, fiat_value: CustodyFee(date=date, value=fiat_value),
        OperationType.DIVIDEND: lambda date, asset, fiat_value: Dividend(date=date, value=fiat_value),
        OperationType.STOCK_SPLIT: lambda date, asset, fiat_value: StockSplit(date=date, stock=asset.asset_name, ratio=int(asset.amount)),
        OperationType.BUY: lambda date, asset, fiat_value: Transaction(date=date, action=Action.BUY, asset=asset.asset_name, fiat_value=fiat_value),
        OperationType.SELL: lambda date, asset, fiat_value: Transaction(date=date, action=Action.SELL, asset=asset.asset_name, fiat_value=fiat_value),

    }

    @classmethod
    def create_operation(
        cls,
        operation_type: OperationType,
        date: pendulum.DateTime,
        asset: Optional[AssetValue] = None,
        fiat_value: Optional[FiatValue] = None,
    ) -> Operation:
        creator = cls._creators.get(operation_type)
        if not creator:
            raise ValueError(f"Invalid operation type: {operation_type}")
        
        return creator(date, asset, fiat_value)
