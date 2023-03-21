import enum


class OperationType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    CUSTODY_FEE = "CUSTODY FEE"
    STOCK_SPLIT = "STOCK SPLIT"

    def __str__(self):
        return self.value
