import pendulum


class StockSplit:
    def __init__(self, date: pendulum.DateTime, stock: str, ratio: int):
        self.date = date
        self.stock = stock
        self.ratio = ratio

    def __str__(self):
        return f"[{self.date.to_date_string()}] Stock {self.stock} split in ratio{self.ratio}:1"
