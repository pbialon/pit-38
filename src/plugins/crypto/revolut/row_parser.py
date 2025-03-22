import re
from typing import Dict
import pendulum
from loguru import logger

from domain.currency_exchange_service.currencies import Currency, CurrencyBuilder, FiatValue
from domain.transactions.action import Action
from domain.transactions.asset import AssetValue
from domain.transactions.transaction import Transaction

BUY_OPERATION_TYPES = ["Buy", "Receive", "Learn reward", "Staking reward"]
SELL_OPERATION_TYPES = ["Sell"]

class RowParser():
    @classmethod
    def parse(cls, row: Dict) -> Transaction:
        action = cls._action(row)
        if action is None:
            logger.debug(f"Skipping transaction: {row}")
            return None
        transaction = Transaction(
            asset=cls._crypto_value(row),
            fiat_value=cls._fiat_value(row),
            action=cls._action(row),
            date=cls._datetime(row),
        )
        logger.info(f"Parsed transaction: {transaction}")
        return transaction

    @classmethod
    def _crypto_value(cls, row: dict) -> AssetValue:
        currency = row["Symbol"]
        amount = row["Quantity"].replace(",", "")
        return AssetValue(float(amount), currency)

    @classmethod
    def _fiat_value(cls, row: dict) -> FiatValue:
        if row["Value"] == "":
            return FiatValue(0, Currency.ZLOTY)

        value = row["Value"].replace(",", "")

        amount_match = re.search(r'\d+\.?\d{2}', value)
        if not amount_match:
            raise ValueError(f"Unable to parse amount: {value}")

        amount_str = amount_match.group()
        currency_str = value.replace(amount_str, "").strip()

        amount = float(amount_match.group())
        currency = CurrencyBuilder.build(currency_str)
        return FiatValue(amount, currency)

    @classmethod
    def _action(cls, row: dict) -> Action:
        if row["Type"] in BUY_OPERATION_TYPES:
            return Action.BUY
        if row["Type"] in SELL_OPERATION_TYPES:
            return Action.SELL
        # Staking and unstaking are not important for tax purposes
        return None

    @classmethod
    def _datetime(cls, row: dict) -> pendulum.DateTime:
        date_str = row["Date"].replace("Sept", "Sep") # revolut uses Sept instead of Sep
        return pendulum.from_format(date_str, "DD MMM YYYY, HH:mm:ss")

