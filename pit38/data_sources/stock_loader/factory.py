import pendulum
from typing import Optional

from pit38.domain.stock.operations.operation import Operation
from pit38.domain.stock.operations.service_fee import ServiceFee
from pit38.domain.stock.operations.dividend import Dividend
from pit38.domain.stock.operations.stock_market_operation import StockMarketOperation
from pit38.domain.stock.operations.stock_split import StockSplit
from pit38.domain.currency_exchange_service.currencies import FiatValue
from pit38.domain.transactions.asset import AssetValue
from pit38.domain.transactions.transaction import Transaction

class OperationFactory:
    _creators = {
        StockMarketOperation.SERVICE_FEE: lambda date, asset, fiat_value: ServiceFee(
            date=date, value=fiat_value,
        ),
        StockMarketOperation.DIVIDEND: lambda date, asset, fiat_value: Dividend(
            date=date, value=fiat_value,
        ),
        StockMarketOperation.STOCK_SPLIT: lambda date, asset, fiat_value: StockSplit(
            date=date, stock=asset.asset_name, ratio=int(asset.amount),
        ),
        StockMarketOperation.BUY: lambda date, asset, fiat_value: Transaction(
            date=date,
            action=StockMarketOperation.BUY.to_action(),
            asset=asset,
            fiat_value=fiat_value,
        ),
        StockMarketOperation.SELL: lambda date, asset, fiat_value: Transaction(
            date=date,
            action=StockMarketOperation.SELL.to_action(),
            asset=asset,
            fiat_value=fiat_value,
        ),
    }

    @classmethod
    def create_operation(
        cls,
        operation_type: StockMarketOperation,
        date: pendulum.DateTime,
        asset: Optional[AssetValue] = None,
        fiat_value: Optional[FiatValue] = None,
    ) -> Operation:
        creator = cls._creators.get(operation_type)
        if not creator:
            raise ValueError(f"Invalid stock market operation: {operation_type}")

        return creator(date, asset, fiat_value)
