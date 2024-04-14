import enum
from typing import Dict

import pendulum
from loguru import logger

from domain.currency_exchange_service.currencies import FiatValue, CurrencyBuilder
from domain.transactions import Transaction, AssetValue, Action
from data_sources.revolut.csv_parser import CsvParser


class State:
    COMPLETED = "COMPLETED"


class OperationType(enum.Enum):
    EXCHANGE = "EXCHANGE"
    REWARD = "REWARD"
    TRANSFER = "TRANSFER"


class CryptoCsvParser(CsvParser):
    @classmethod
    def parse(cls, row: Dict) -> Transaction:
        if not CryptoCsvParser._is_completed(row):
            logger.debug(f"Skipping transaction: {row} (not completed)")
            return None
        operation_type = cls._operation_type(row)
        if operation_type == OperationType.TRANSFER:
            logger.debug(f"Skipping transaction: {row} (transfer)")
            return None
        transaction = Transaction(
            asset=CryptoCsvParser.crypto_value(row),
            fiat_value=cls.fiat_value_of_transaction(row, operation_type),
            action=CryptoCsvParser.action(row),
            date=CryptoCsvParser.datetime(row),
        )
        logger.debug(f"Parsed transaction: {transaction}")
        return transaction

    @classmethod
    def fiat_value_of_transaction(
        cls, row: dict, operation_type: OperationType
    ) -> FiatValue:
        fiat_value = cls.fiat_value(row)
        if operation_type == OperationType.EXCHANGE:
            return fiat_value
        # operation_type == OperationType.REWARD
        return FiatValue(0, fiat_value.currency)

    @classmethod
    def crypto_value(cls, row: dict) -> AssetValue:
        currency = row["Currency"]
        amount = abs(float(row["Amount"]))
        return AssetValue(amount, currency)

    @classmethod
    def fiat_value(cls, row: dict) -> FiatValue:
        currency = CurrencyBuilder.build(row["Base currency"])
        amount = abs(float(row["Fiat amount (inc. fees)"]))
        return FiatValue(amount, currency)

    @classmethod
    def action(cls, row: dict) -> Action:
        target_currency = row["Description"].split(" ")[-1]
        is_fiat_currency = target_currency in CurrencyBuilder.CURRENCIES

        if is_fiat_currency:
            return Action.SELL
        return Action.BUY

    @classmethod
    def datetime(cls, row: dict) -> pendulum.DateTime:
        raw_datetime = CryptoCsvParser._clean_up_datetime(row["Completed Date"])
        return pendulum.parse(raw_datetime)

    @classmethod
    def _is_completed(cls, row: dict) -> bool:
        return row["State"] == State.COMPLETED

    @classmethod
    def _operation_type(cls, row):
        if row["Type"] == "EXCHANGE":
            return OperationType.EXCHANGE
        if row["Type"] == "REWARD":
            return OperationType.REWARD
        if row["Type"] == "TRANSFER":
            return OperationType.TRANSFER

    @classmethod
    def _clean_up_datetime(cls, raw_datetime: str) -> str:
        # add 0 in front of hour if needed
        date, time = raw_datetime.split(" ")
        hours, minutes, seconds = time.split(":")
        if len(hours) == 1:
            return f"{date} 0{hours}:{minutes}:{seconds}"
        return raw_datetime
