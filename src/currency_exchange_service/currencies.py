import enum

from revolut.crypto.invalid_currency_exception import InvalidCurrencyException


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
    def __init__(self, amount: float, currency: Currency):
        self.amount = amount
        self.currency = currency

    def __str__(self):
        return f"{self.amount} {self.currency}"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
