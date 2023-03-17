import pendulum

from domain.currency_exchange_service.currencies import FiatValue


class Dividend:
    TYPE = "DIVIDENDS"

    def __init__(self, date: pendulum.DateTime, value: FiatValue):
        self.date = date
        self.value = value

    def __str__(self):
        return f"{self.date.to_date_string()}: {self.value}"
