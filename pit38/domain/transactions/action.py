import enum
from typing import List


class Action(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other.value

    @classmethod
    def available_actions(cls) -> List[str]:
        # BUY, SELL
        return [action.value for action in cls]
