import enum


class Operation:
    type = None


class OperationType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    CUSTODY_FEE = "CUSTODY_FEE"
    STOCK_SPLIT = "STOCK_SPLIT"

    def __str__(self):
        return self.value
