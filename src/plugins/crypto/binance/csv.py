import csv
from datetime import datetime
from enum import Enum
from typing import List

import pendulum
from loguru import logger
from domain.currency_exchange_service.currencies import CurrencyBuilder, FiatValue
from domain.transactions.action import Action
from domain.transactions.asset import AssetValue
from domain.transactions.transaction import Transaction


class BinanceOperationType(Enum):
    CONVERT = "Binance Convert"
    TRANSACTION = "Transaction"
    DEPOSIT = "Deposit"


class BinanceTransaction:
    def __init__(self, row: dict):
        self.utc_time = datetime.strptime(row["UTC_Time"], "%Y-%m-%d %H:%M:%S")
        self.operation = row["Operation"]
        self.coin = row["Coin"]
        self.change = float(row["Change"])
        
    def operation_type(self) -> BinanceOperationType:
        if self.operation == BinanceOperationType.CONVERT.value:
            return BinanceOperationType.CONVERT
        elif self.operation == BinanceOperationType.DEPOSIT.value:
            return BinanceOperationType.DEPOSIT
        elif self.operation.startswith(BinanceOperationType.TRANSACTION.value):
            return BinanceOperationType.TRANSACTION

        raise ValueError(f"Unknown operation type: {self.operation}")


class BinanceTransactionProcessor:
    def _process_convert_transactions(self, binance_transactions: List[BinanceTransaction]) -> List[Transaction]:
        fiat_currencies_list = CurrencyBuilder.CURRENCIES.keys()
        return [
            Transaction(
                asset=AssetValue(abs(crypto_tx.change), crypto_tx.coin),
                fiat_value=FiatValue(abs(fiat_tx.change), fiat_tx.coin),
                action=Action.SELL if crypto_tx.change < 0 else Action.BUY,
                # TODO: handle datezone
                date=pendulum.instance(current_tx.utc_time)
            )
            for current_tx, next_tx in zip(binance_transactions[::2], binance_transactions[1::2])
            for fiat_tx, crypto_tx in [(current_tx, next_tx) if current_tx.coin in fiat_currencies_list else (next_tx, current_tx)]
        ]

    def _process_transaction_operations(self, binance_transactions: List[BinanceTransaction]) -> List[Transaction]:
        # TODO: handle sell operations
        transactions = []
        for group in zip(binance_transactions[::3], binance_transactions[1::3], binance_transactions[2::3]):
            buy_tx = next(tx for tx in group if tx.operation == "Transaction Buy")
            fee_tx = next(tx for tx in group if tx.operation == "Transaction Fee")
            spend_tx = next(tx for tx in group if tx.operation == "Transaction Spend")
            
            if not buy_tx or not fee_tx or not spend_tx:
                logger.warning(f"Skipping transaction group: {group}")
                continue
            
            transactions.append(Transaction(
                asset=AssetValue(buy_tx.change + fee_tx.change, buy_tx.coin),
                fiat_value=FiatValue(spend_tx.change, spend_tx.coin),
                action=Action.BUY,
                # TODO: handle datezone
                date=pendulum.instance(buy_tx.utc_time)
            ))
        
        return transactions

    def read(self, file_path: str) -> List[Transaction]:
        convert_operations = []
        transaction_operations = []
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                binance_transaction = BinanceTransaction(row)
                if binance_transaction.operation_type() == BinanceOperationType.DEPOSIT:
                    continue

                if binance_transaction.operation_type() == BinanceOperationType.CONVERT:
                    convert_operations.append(binance_transaction)
                elif binance_transaction.operation_type() == BinanceOperationType.TRANSACTION:
                    transaction_operations.append(binance_transaction)
        
        all_transactions = self._process_convert_transactions(convert_operations) + self._process_transaction_operations(transaction_operations)

        return sorted(all_transactions, key=lambda x: x.date) 
    
