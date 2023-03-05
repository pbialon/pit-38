import enum


class Currency(enum.Enum):
    DOLLAR = "USD"
    EURO = "EUR"
    ZLOTY = "PLN"

    def __str__(self):
        return self.value


class FiatValue:
    def __init__(self, amount: float, currency: Currency):
        self.amount = amount
        self.currency = currency

    def __str__(self):
        return f"{self.amount} {self.currency}"
