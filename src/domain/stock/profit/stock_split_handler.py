from typing import List

import pendulum
from loguru import logger

from domain.stock.operations.stock_split import StockSplit
from domain.transactions import Transaction


class StockSplitHandler:
    @classmethod
    def multiplier_for_date(cls, stock_splits: List[StockSplit], date: pendulum.DateTime) -> float:
        multiplier = 1
        for stock_split in reversed(stock_splits):
            if stock_split.date > date:
                multiplier *= stock_split.ratio
        if multiplier > 1:
            logger.debug(f"Stock split multiplier for {date} is {multiplier}")
        return multiplier

    @classmethod
    def incorporate_stock_splits_into_transactions(cls,
                                                   transactions: List[Transaction],
                                                   stock_splits: List[StockSplit]) -> List[Transaction]:
        if not stock_splits:
            return transactions
        logger.info(f"Handling {len(stock_splits)} stock splits")
        cls._assert_the_same_company(transactions, stock_splits)
        transactions, stock_splits = cls._sort_by_date(transactions, stock_splits)

        new_transactions = []
        for transaction in transactions:
            multiplier = cls.multiplier_for_date(stock_splits, transaction.date)
            adjusted_transaction = cls._adjust_transaction(transaction, multiplier)
            new_transactions.append(adjusted_transaction)
        logger.debug(f"Transactions after handling stock splits: {new_transactions}")
        return new_transactions

    @classmethod
    def _adjust_transaction(cls, transaction: Transaction, multiplier: float) -> Transaction:
        return Transaction(
            transaction.asset * multiplier,
            transaction.fiat_value,
            transaction.action,
            transaction.date,
        )

    @classmethod
    def _sort_by_date(cls, transactions: List[Transaction], stock_splits: List[StockSplit]) \
            -> (List[Transaction], List[StockSplit]):

        by_date = lambda x: x.date
        return sorted(transactions, key=by_date), sorted(stock_splits, key=by_date)

    @classmethod
    def _assert_the_same_company(cls, transactions: List[Transaction], stock_splits: List[StockSplit]):
        assert (t.asset.asset_name == transactions[0].asset.asset_name for t in transactions), \
            "All transactions should be from the same company"
        assert (split.stock == stock_splits[0].stock for split in stock_splits), \
            "All stock splits should be for the same stock"
        assert transactions[0].asset.asset_name == stock_splits[0].stock, \
            "All operations should be from the same company"
