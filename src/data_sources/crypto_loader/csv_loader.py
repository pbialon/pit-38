import csv
from typing import List, Optional
import pendulum
from loguru import logger

from domain.transactions import Transaction, AssetValue, Action
from domain.currency_exchange_service.currencies import FiatValue, Currency

class Loader:
    @classmethod
    def load(cls, file_path: str) -> List[Transaction]:
        transactions = []
        logger.info(f"Loading transactions from {file_path}...")
        
        with open(file_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                transaction = cls._parse_row(row)
                if transaction:
                    logger.debug(f"Parsed transaction: {transaction}")
                    transactions.append(transaction)

        logger.info(f"Loaded {len(transactions)} transactions")
        return transactions

    @classmethod
    def _parse_row(cls, row: dict) -> Optional[Transaction]:
        try:
            transaction = Transaction(
                asset=cls._asset_value(row),
                fiat_value=cls._fiat_value(row),
                action=cls._action(row),
                date=cls._datetime(row)
            )
            return transaction
        except (ValueError, KeyError) as e:
            logger.warning(f"Skipping invalid row: {row}. Error: {str(e)}")
            return None

    @classmethod
    def _asset_value(cls, row: dict) -> AssetValue:
        try:
            amount = float(row["amount"])
            symbol = row["symbol"]
            if not symbol:
                raise ValueError("Cryptocurrency symbol cannot be empty")
            return AssetValue(amount, symbol)
        except (ValueError, KeyError) as e:
            raise ValueError(f"Failed to parse cryptocurrency value: {str(e)}")

    @classmethod
    def _fiat_value(cls, row: dict) -> FiatValue:
        try:
            amount = float(row["fiat_value"])
            return FiatValue(amount, Currency.ZLOTY)
        except (ValueError, KeyError) as e:
            raise ValueError(f"Failed to parse fiat value: {str(e)}")

    @classmethod
    def _action(cls, row: dict) -> Action:
        try:
            action = row["operation"]
            if action not in Action.available_actions():
                raise ValueError(f"Unknown operation: {action}")
            return Action[action]
        except (KeyError, ValueError) as e:
            raise ValueError(f"Failed to parse operation type: {str(e)}")

    @classmethod
    def _datetime(cls, row: dict) -> pendulum.DateTime:
        try:
            return pendulum.parse(row["date"])
        except (ValueError, KeyError) as e:
            raise ValueError(f"Failed to parse date: {str(e)}") 