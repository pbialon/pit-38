import csv
from typing import Dict, List, Tuple
from loguru import logger
import pendulum

from pit38.domain.transactions.action import Action
from pit38.domain.transactions.asset import AssetValue
from pit38.domain.transactions.transaction import Transaction
from pit38.plugins.stock.etrade.row_parser import FiatValueParser


class CsvService:
    @classmethod
    def read(cls, file_path: str) -> List[Transaction]:
        transactions = []
        logger.info(f"Reading transactions from {file_path}...")
        with open(file_path, "r") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=",")
            for row in reader:
                if row["Record Type"] == "Summary":
                    continue
                buy, sell = cls.parse_row(row)
                transactions.extend((buy, sell))

        logger.info(f"Parsed {len(transactions)} transactions")
        return transactions

    @classmethod
    def parse_row(cls, row: Dict) -> Tuple[Transaction, Transaction]:
        buy = cls._buy_transaction(row)
        logger.debug(f"Parsed buy transaction: {buy}")

        sell = cls._sell_transaction(row)
        logger.debug(f"Parsed sell transaction: {sell}")

        return buy, sell
    
    @classmethod
    def _buy_transaction(cls, row: Dict) -> Transaction:
        return Transaction(
            asset=cls._asset(row),
            fiat_value=cls._buy_cost(row),
            action=Action.BUY,
            date=pendulum.parse(str(row["Date Acquired"]), strict=False),
        )
        
    @classmethod
    def _sell_transaction(cls, row: Dict) -> Transaction:
        return Transaction(
            asset=cls._asset(row),
            fiat_value=cls._sell_cost(row),
            action=Action.SELL,
            date=pendulum.parse(str(row["Date Sold"]), strict=False),
        )

    @classmethod
    def _asset(cls, row: Dict) -> AssetValue:
        quantity = float(row['Qty.'])
        stock_name = row['Symbol']
        return AssetValue(quantity, stock_name)
    
    def _buy_cost(row: Dict) -> float:
        return FiatValueParser.parse(row["Acquisition Cost"])
    
    def _sell_cost(row: Dict) -> float:
        return FiatValueParser.parse(row["Total Proceeds"]) 