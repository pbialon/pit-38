import pendulum

from pit38.domain.currency_exchange_service.currencies import FiatValue
from pit38.domain.stock.operations.operation import Operation, OperationType


class ServiceFee(Operation):
    type = OperationType.SERVICE_FEE

    def __init__(self, date: pendulum.DateTime, value: FiatValue):
        self.date = date
        self.value = value

    def __str__(self):
        return f"{self.date.to_date_string()}: service fee = {self.value}"
