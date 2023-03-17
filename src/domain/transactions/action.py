import enum


class Action(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other.value

