import pendulum

from data_sources.revolut.stock.operation import OperationType
from domain.currency_exchange_service.currencies import FiatValue
from domain.stock.operation import Operation


class CustodyFee(Operation):
    type = OperationType.CUSTODY_FEE

    def __init__(self, date: pendulum.DateTime, value: FiatValue):
        self.date = date
        self.value = value

    def __str__(self):
        return f"{self.date.to_date_string()}: custody fee = {self.value}"