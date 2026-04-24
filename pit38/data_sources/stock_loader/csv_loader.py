import csv
from typing import List, Optional
import pendulum
from loguru import logger

from pit38.domain.stock.operations.operation import Operation, OperationType
from pit38.data_sources.stock_loader.factory import OperationFactory
from pit38.domain.currency_exchange_service.currencies import parse_currency, FiatValue, InvalidCurrencyException
from pit38.domain.transactions.asset import AssetValue
from pit38.domain.transactions.transaction import Transaction

class Loader:
    @classmethod
    def load(cls, file_path: str) -> List[Operation | Transaction]:
        operations = []
        logger.info(f"Loading stock operations from {file_path}...")
        
        with open(file_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                operation = cls._parse_row(row)
                if operation:
                    logger.debug(f"Parsed operation: {operation}")
                    operations.append(operation)

        logger.info(f"Loaded {len(operations)} operations")
        return operations

    @classmethod
    def _parse_row(cls, row: dict) -> Optional[Operation | Transaction]:
        try:
            operation_type = cls._operation_type(row)
            date = cls._datetime(row)
            asset = cls._asset_value(row) if cls._requires_symbol(row) else None
            fiat_value = cls._fiat_value(row)

            return OperationFactory.create_operation(
                operation_type=operation_type,
                date=date,
                asset=asset,
                fiat_value=fiat_value
            )
        except (ValueError, KeyError) as e:
            logger.warning(f"Skipping invalid row: {row}. Error: {str(e)}")
            return None

    @classmethod
    def _asset_value(cls, row: dict) -> AssetValue:
        try:
            amount = float(row["amount"]) if row["amount"] else 0.0
            symbol = row["symbol"]
            if not symbol and cls._requires_symbol(row):
                raise ValueError("Stock symbol cannot be empty")
            return AssetValue(amount, symbol)
        except (ValueError, KeyError) as e:
            raise ValueError(f"Failed to parse asset value: {str(e)}")

    @classmethod
    def _requires_symbol(cls, row: dict) -> bool:
        operation = row.get("operation", "")
        return operation not in ["SERVICE_FEE", "DIVIDEND"]

    @classmethod
    def _fiat_value(cls, row: dict) -> Optional[FiatValue]:
        try:
            if not row.get("fiat_value"):
                return None
            amount = float(row["fiat_value"])
            currency = parse_currency(row["currency"])
            return FiatValue(amount, currency)
        except (ValueError, KeyError) as e:
            raise ValueError(f"Failed to parse fiat value: {str(e)}")
        except InvalidCurrencyException as e:
            raise ValueError(f"Failed to parse currency: {str(e)}")

    @classmethod
    def _operation_type(cls, row: dict) -> OperationType:
        try:
            return OperationType[row["operation"]]
        except (KeyError, ValueError) as e:
            raise ValueError(f"Failed to parse operation type: {str(e)}")

    @classmethod
    def _datetime(cls, row: dict) -> pendulum.DateTime:
        try:
            return pendulum.parse(row["date"])
        except (ValueError, KeyError) as e:
            raise ValueError(f"Failed to parse date: {str(e)}") 