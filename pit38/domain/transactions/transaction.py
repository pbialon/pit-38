import pendulum

from pit38.domain.currency_exchange_service.currencies import FiatValue
from pit38.domain.transactions.action import Action
from pit38.domain.transactions.asset import AssetValue


class Transaction:
    def __init__(self,
                 asset: AssetValue,
                 fiat_value: FiatValue,
                 action: Action,
                 date: pendulum.DateTime):
        self.fiat_value = fiat_value
        self.asset = asset
        self.action = action
        self.date = date

    @property
    def year(self) -> int:
        return self.date.year

    def __str__(self):
        if self.action == Action.BUY:
            return f"[{self.date.to_date_string()}]: {self.fiat_value} => {self.action} {self.asset}"
        # Action.SELL
        return f"[{self.date.to_date_string()}]: {self.action} {self.asset} => {self.fiat_value}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Transaction(
                self.asset * other,
                self.fiat_value * other,
                self.action,
                self.date,
            )
        raise TypeError("Cannot multiply by non-numeric value")
