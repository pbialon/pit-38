import csv

import pendulum

from domain.currency_exchange_service.currencies import FiatValue, CurrencyBuilder
from domain.crypto.transaction import Transaction, CryptoValue, Action


class State:
    COMPLETED = "COMPLETED"


class TsvParser:
    @staticmethod
    def parse(row: dict) -> Transaction:
        if not TsvParser._is_completed(row):
            return None
        return Transaction(
            crypto_value=TsvParser.crypto_value(row),
            fiat_value=TsvParser.fiat_value(row),
            action=TsvParser.action(row),
            date=TsvParser.date(row)
        )

    @staticmethod
    def crypto_value(row: dict) -> CryptoValue:
        currency = row['Currency']
        amount = abs(float(row['Amount']))
        return CryptoValue(amount, currency)

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
        raw_datetime = TsvParser._clean_up_datetime(row['Completed Date'])
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


class TsvReader:
    def __init__(self, path: str, tsv_parser: TsvParser):
        self.path = path
        self.tsv_parser = tsv_parser

    def read(self):
        with open(self.path, 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t')
            for row in reader:
                transaction = self.tsv_parser.parse(row)
                if not transaction:
                    continue

                yield transaction
