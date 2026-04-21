from typing import Dict, List, Tuple
from loguru import logger
import pendulum

from pit38.data_sources.csv_utils import open_csv_reader
from pit38.domain.currency_exchange_service.currencies import FiatValue
from pit38.domain.transactions.action import Action
from pit38.domain.transactions.asset import AssetValue
from pit38.domain.transactions.transaction import Transaction
from pit38.plugins.stock.etrade.row_parser import FiatValueParser


class EtradeCsvReader:
    @classmethod
    def read(cls, file_path: str) -> List[Transaction]:
        transactions = []
        logger.info(f"Reading transactions from {file_path}...")
        with open_csv_reader(file_path) as reader:
            for row in reader:
                if row["record type"] == "Summary":
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
            date=pendulum.parse(str(row["date acquired"]), strict=False),
        )

    @classmethod
    def _sell_transaction(cls, row: Dict) -> Transaction:
        return Transaction(
            asset=cls._asset(row),
            fiat_value=cls._sell_cost(row),
            action=Action.SELL,
            date=pendulum.parse(str(row["date sold"]), strict=False),
        )

    @classmethod
    def _asset(cls, row: Dict) -> AssetValue:
        quantity = float(row['qty.'])
        stock_name = row['symbol']
        return AssetValue(quantity, stock_name)

    @classmethod
    def _buy_cost(cls, row: Dict) -> FiatValue:
        return FiatValueParser.parse(row["acquisition cost"])

    @classmethod
    def _sell_cost(cls, row: Dict) -> FiatValue:
        return FiatValueParser.parse(row["total proceeds"])