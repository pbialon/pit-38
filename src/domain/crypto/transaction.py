import enum

import pendulum

from currency_exchange_service.currencies import FiatValue


class Action(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

    def __str__(self):
        return self.value


class CryptoValue:
    def __init__(self, amount: float, currency: str):
        self.amount = amount
        self.currency = currency

    def __str__(self):
        return f"{self.amount} {self.currency}"


class Transaction:
    def __init__(self,
                 crypto_value: CryptoValue,
                 fiat_value: FiatValue,
                 action: Action,
                 date: pendulum.DateTime):
        self.fiat_value = fiat_value
        self.crypto_value = crypto_value
        self.action = action
        self.date = date

    def __str__(self):
        if self.action == Action.BUY:
            return f"[{self.date.to_date_string()}]: {self.fiat_value} => {self.crypto_value}"
        # Action.SELL
        return f"[{self.date.to_date_string()}]: {self.action} {self.crypto_value} => {self.fiat_value}"
