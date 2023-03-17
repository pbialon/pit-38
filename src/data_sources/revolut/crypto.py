import csv
from typing import List

import pendulum
from loguru import logger

from domain.currency_exchange_service.currencies import FiatValue, CurrencyBuilder
from domain.transactions import Transaction, AssetValue, Action


class State:
    COMPLETED = "COMPLETED"


class CsvParser:
    @staticmethod
    def parse(row: dict) -> Transaction:
        if not CsvParser._is_completed(row):
            logger.debug(f'Skipping transaction: {row} (not completed)')
            return None
        transaction = Transaction(
            asset=CsvParser.crypto_value(row),
            fiat_value=CsvParser.fiat_value(row),
            action=CsvParser.action(row),
            date=CsvParser.date(row)
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
        raw_datetime = CsvParser._clean_up_datetime(row['Completed Date'])
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


class CsvReader:
    def __init__(self, path: str, csv_parser: CsvParser):
        self.path = path
        self.csv_parser = csv_parser

    def read(self) -> List[Transaction]:
        transactions = []
        logger.info(f"Reading transactions from {self.path}...")
        with open(self.path, 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for row in reader:
                transaction = self.csv_parser.parse(row)
                if not transaction:
                    continue

                transactions.append(transaction)
        logger.info(f"Parsed {len(transactions)} transactions")
        return transactions
