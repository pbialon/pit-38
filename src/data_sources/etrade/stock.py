import csv
from typing import Dict, List, Tuple
from loguru import logger
import pendulum

from data_sources.etrade.fiat_value_parser import FiatValueParser
from domain.transactions.action import Action
from domain.transactions.asset import AssetValue
from domain.transactions.transaction import Transaction


class StockCsvReader:
    @classmethod
    def read(cls, file_path: str) -> List[Transaction]:
        """
        Get stock data from the csv file
        """
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
        """
        Parse a row from the DataFrame into a Transaction object
        """
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
