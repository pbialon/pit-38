from typing import List

import pendulum
from loguru import logger

from domain.stock.operations.stock_split import StockSplit
from domain.transactions import Transaction


class StockSplitHandler:
    @classmethod
    def multiplier_for_date(cls, stock_splits: List[StockSplit], date: pendulum.DateTime) -> float:
        assert sorted(stock_splits) == stock_splits, "It should be sorted"
        assert all(stock_split.stock == stock_splits[0].stock for stock_split in stock_splits), \
            "All stock splits should be for the same stock"

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
        sort_by_date = lambda x: x.date

        stock_splits.sort(key=sort_by_date)
        transactions.sort(key=sort_by_date)

        assert set(split.stock for split in stock_splits) == \
               set(transaction.asset.asset_name for transaction in transactions), \
            "All stock splits should be for the same stock"

        new_transactions = []
        for transaction in transactions:
            multiplier = cls.multiplier_for_date(stock_splits, transaction.date)
            new_transactions.append(Transaction(
                transaction.asset * multiplier,
                transaction.fiat_value,
                transaction.action,
                transaction.date,
            ))

        return new_transactions
