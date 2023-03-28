from typing import List

import pendulum
from loguru import logger

from domain.stock.operations.stock_split import StockSplit


class StockSplitHandler:
    @classmethod
    def multiplier_for_date(cls, stock_splits: List[StockSplit], date: pendulum.DateTime) -> float:
        assert sorted(stock_splits) == stock_splits, "It should be sorted"

        multiplier = 1
        for stock_split in reversed(stock_splits):
            if stock_split.date > date:
                multiplier *= stock_split.ratio
        if multiplier > 1:
            logger.debug(f"Stock split multiplier for {date} is {multiplier}")
        return multiplier
