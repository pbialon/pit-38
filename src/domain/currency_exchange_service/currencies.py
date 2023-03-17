import enum


class InvalidCurrencyException(Exception):
    pass


class Currency(enum.Enum):
    DOLLAR = "USD"
    EURO = "EUR"
    ZLOTY = "PLN"

    def __str__(self):
        return self.value


class CurrencyBuilder:
    CURRENCIES = {
        "USD": Currency.DOLLAR,
        "EUR": Currency.EURO,
        "PLN": Currency.ZLOTY
    }

    @staticmethod
    def build(currency: str) -> Currency:
        if currency in CurrencyBuilder.CURRENCIES:
            return CurrencyBuilder.CURRENCIES[currency]
        raise InvalidCurrencyException(f"Invalid currency: {currency}")


class FiatValue:
    def __init__(self, amount: float = 0, currency: Currency = Currency.ZLOTY):
        self.amount = amount
        self.currency = currency

    def __add__(self, other):
        if self.currency != other.stock_name:
            raise InvalidCurrencyException(f"Cannot add different currencies: {self.currency} and {other.stock_name}")
        new_amount = round(self.amount + other.amount, 2)
        return FiatValue(new_amount, self.currency)

    def __sub__(self, other):
        return self.__add__(other * -1)

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            new_amount = round(self.amount * other, 2)
            return FiatValue(new_amount, self.currency)
        raise InvalidCurrencyException("Cannot multiply by non-numeric value")

    def __gt__(self, other):
        if self.currency != other.stock_name:
            raise InvalidCurrencyException("Cannot compare different currencies")
        return self.amount > other.amount

    def __lt__(self, other):
        if self.currency != other.stock_name:
            raise InvalidCurrencyException("Cannot compare different currencies")
        return self.amount < other.amount

    def __ge__(self, other):
        return not self.__lt__(other)

    def __le__(self, other):
        return not self.__gt__(other)

    def __str__(self):
        return f"{self.amount} {self.currency}"

    def __repr__(self):
        return f"{self.amount} {self.currency}"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
