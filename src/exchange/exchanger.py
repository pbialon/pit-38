import pendulum
from src.calendar_manager.holidays_provider import get_holidays

EXCHANGE_RATEST_FILENAME = "/Users/pbialon/workbench/pit/resources/exchange_rates.csv"


class Exchanger:
    def __init__(self):
        self.exchange_rates = self._read_dolar_exchange_rates_from_file(EXCHANGE_RATEST_FILENAME)

    def exchange(self, date: pendulum.DateTime, amount: float) -> float:
        exchange_day = self.get_day_one(date)
        return round(amount * self.exchange_rates[exchange_day], 2)

    def _read_dolar_exchange_rates_from_file(self, filename: str):
        exchange_rates = {}
        with open(filename, "r") as f:
            for line in f:
                line = line.split(";")
                date, rate = pendulum.parse(line[0]).date(), float(line[2].replace(",", "."))
                exchange_rates[date] = rate
        return exchange_rates

    @staticmethod
    def get_day_one(date: pendulum.DateTime) -> pendulum.Date:
        date = date.subtract(days=1)

        while not Exchanger.is_workday(date):
            date = date.subtract(days=1)

        if date < pendulum.parse("2021-01-01"):
            raise ValueError("Date is before 2021-01-01")

        return date.date()

    @staticmethod
    def is_workday(date: pendulum.DateTime):
        if date.format("E") in ("6", "7"):
            # Saturday or Sunday
            return False
        if date in get_holidays():
            return False
        return True
