from typing import Dict

import pendulum
from loguru import logger

from domain.currency_exchange_service.currencies import FiatValue, CurrencyBuilder
from domain.transactions import Transaction, AssetValue, Action
from data_sources.revolut.csv_reader import CsvParser


class State:
    COMPLETED = "COMPLETED"


class CryptoCsvParser(CsvParser):
    @staticmethod
    def parse(row: Dict) -> Transaction:
        if not CryptoCsvParser._is_completed(row):
            logger.debug(f'Skipping transaction: {row} (not completed)')
            return None
        transaction = Transaction(
            asset=CryptoCsvParser.crypto_value(row),
            fiat_value=CryptoCsvParser.fiat_value(row),
            action=CryptoCsvParser.action(row),
            date=CryptoCsvParser.date(row)
        )
        logger.debug(f'Parsed transaction: {transaction}')
        return transaction

    @staticmethod
    def crypto_value(row: dict) -> AssetValue:
        currency = row['Currency']
        amount = abs(float(row['Amount']))
        return AssetValue(amount, currency)

    @staticmethod
    def fiat_value(row: dict) -> FiatValue:
        currency = CurrencyBuilder.build(row['Base currency'])
        amount = abs(float(row['Fiat amount (inc. fees)']))
        return FiatValue(amount, currency)

    @staticmethod
    def action(row: dict) -> Action:
        target_currency = row['Description'].split(' ')[-1]
        is_fiat_currency = target_currency in CurrencyBuilder.CURRENCIES

        if is_fiat_currency:
            return Action.SELL
        return Action.BUY

    @staticmethod
    def date(row: dict) -> pendulum.DateTime:
        raw_datetime = CryptoCsvParser._clean_up_datetime(row['Completed Date'])
        return pendulum.parse(raw_datetime)

    @staticmethod
    def _is_completed(row: dict) -> bool:
        return row['State'] == State.COMPLETED

    @staticmethod
    def _clean_up_datetime(raw_datetime: str) -> str:
        # add 0 in front of hour if needed
        date, time = raw_datetime.split(' ')
        hours, minutes, seconds = time.split(':')
        if len(hours) == 1:
            return f"{date} 0{hours}:{minutes}:{seconds}"
        return raw_datetime
