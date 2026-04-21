import enum
from typing import List

from pit38.domain.transactions.action import Action


class StockMarketOperation(enum.Enum):
    """Classification of a row in a stock-market CSV.

    Includes transactions (BUY/SELL), income events (DIVIDEND),
    service costs (SERVICE_FEE), and corporate actions (STOCK_SPLIT).

    Crypto CSVs do not use this enum — crypto rows only represent
    transactions, so they're classified by Action directly.
    """
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    SERVICE_FEE = "SERVICE_FEE"
    STOCK_SPLIT = "STOCK_SPLIT"

    def __str__(self):
        return self.value

    def is_transaction(self) -> bool:
        return self in (StockMarketOperation.BUY, StockMarketOperation.SELL)

    def to_action(self) -> Action:
        """Convert a transactional operation into the common Action enum.

        Raises ValueError for non-transactional operations (DIVIDEND,
        SERVICE_FEE, STOCK_SPLIT).
        """
        if self is StockMarketOperation.BUY:
            return Action.BUY
        if self is StockMarketOperation.SELL:
            return Action.SELL
        raise ValueError(f"{self} is not a transactional operation")

    @classmethod
    def available_operations(cls) -> List[str]:
        return [op.value for op in cls]
