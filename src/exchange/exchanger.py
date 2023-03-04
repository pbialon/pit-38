import pendulum

from calendar_manager.calendar import Calendar

EXCHANGE_RATES_FILENAME = "/Users/pbialon/workbench/pit/resources/exchange_rates.csv"


class Exchanger:
    def __init__(self, calendar: Calendar):
        self.exchange_rates = self._read_dollar_exchange_rates_from_file(EXCHANGE_RATES_FILENAME)
        self.calendar = calendar

    def exchange(self, date: pendulum.DateTime, amount: float) -> float:
        exchange_day = self.get_day_one(date)
        return round(amount * self.exchange_rates[exchange_day], 2)

    def _read_dollar_exchange_rates_from_file(self, filename: str):
        exchange_rates = {}
        with open(filename, "r") as f:
            for line in f:
                line = line.split(";")
                day, rate = pendulum.parse(line[0]).date(), float(line[2].replace(",", "."))
                exchange_rates[day] = rate
        return exchange_rates

    def get_day_one(self, day: pendulum.DateTime) -> pendulum.Date:
        day = day.subtract(days=1)

        while not self.calendar.is_workday(day):
            day = day.subtract(days=1)

        if self.calendar.is_out_of_range(day):
            raise ValueError("Date {} is out of range".format(day))

        return day.date()
