import pendulum

from pit38.domain.stock.operations.operation import Operation, OperationType


class StockSplit(Operation):
    type = OperationType.STOCK_SPLIT

    def __init__(self, date: pendulum.DateTime, stock: str, ratio: int):
        self.date = date
        self.stock = stock
        self.ratio = ratio

    def __str__(self):
        return f"[{self.date.to_date_string()}] Stock {self.stock} split in ratio {self.ratio}:1"

    def __gt__(self, other):
        return self.date > other.date

    def __repr__(self):
        return self.__str__()
