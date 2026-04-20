import pendulum
from typing import Optional

from pit38.domain.stock.operations.operation import Operation, OperationType
from pit38.domain.stock.operations.service_fee import ServiceFee
from pit38.domain.stock.operations.dividend import Dividend
from pit38.domain.stock.operations.stock_split import StockSplit
from pit38.domain.currency_exchange_service.currencies import FiatValue
from pit38.domain.transactions.action import Action
from pit38.domain.transactions.asset import AssetValue
from pit38.domain.transactions.transaction import Transaction

class OperationFactory:
    _creators = {
        OperationType.SERVICE_FEE: lambda date, asset, fiat_value: ServiceFee(date=date, value=fiat_value),
        OperationType.DIVIDEND: lambda date, asset, fiat_value: Dividend(date=date, value=fiat_value),
        OperationType.STOCK_SPLIT: lambda date, asset, fiat_value: StockSplit(date=date, stock=asset.asset_name, ratio=int(asset.amount)),
        OperationType.BUY: lambda date, asset, fiat_value: Transaction(date=date, action=Action.BUY, asset=asset, fiat_value=fiat_value),
        OperationType.SELL: lambda date, asset, fiat_value: Transaction(date=date, action=Action.SELL, asset=asset, fiat_value=fiat_value),

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
