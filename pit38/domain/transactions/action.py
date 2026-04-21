import enum
from typing import List


class Action(enum.Enum):
    """Transaction action: what the user did with an asset.

    Common to both stocks and crypto — every Transaction has an action.
    Non-transactional events on the stock market (dividends, fees, splits)
    are classified separately via StockMarketOperation.
    """
    BUY = "BUY"
    SELL = "SELL"

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if other is None:
            return False
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    @classmethod
    def available_actions(cls) -> List[str]:
        return [action.value for action in cls]
