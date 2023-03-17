import enum

import pendulum

from domain.currency_exchange_service.currencies import FiatValue
from domain.transactions.action import Action


class StockValue:
    def __init__(self, amount: float, stock_name: str):
        self.amount = amount
        self.stock_name = stock_name

    def __str__(self):
        return f"{self.amount} {self.stock_name}"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Transaction:
    def __init__(self,
                 stock_value: StockValue,
                 fiat_value: FiatValue,
                 action: Action,
                 date: pendulum.DateTime):
        self.fiat_value = fiat_value
        self.stock_value = stock_value
        self.action = action
        self.date = date

    def __str__(self):
        if self.action == Action.BUY:
            return f"[{self.date.to_date_string()}]: {self.fiat_value} => {self.action} {self.stock_value}"
        # Action.SELL
        return f"[{self.date.to_date_string()}]: {self.action} {self.stock_value} => {self.fiat_value}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
