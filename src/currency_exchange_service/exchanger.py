import pendulum

from calendar_service.calendar import Calendar
from currency_exchange_service.currencies import Currency, FiatValue
from currency_exchange_service.exchange_rates_provider import ExchangeRatesProvider


class Exchanger:
    def __init__(self, exchange_rates_provider: ExchangeRatesProvider, calendar: Calendar):
        self.exchange_rates_provider = exchange_rates_provider
        self.calendar = calendar
        # TODO: dependency injection
        self.base_currency = Currency.ZLOTY

    def exchange(self, date: pendulum.DateTime, fiat_value: FiatValue) -> float:
        exchange_day = self.get_day_one(date)
        rate = self.exchange_rates_provider.get_rate(fiat_value.currency, exchange_day)
        return round(fiat_value.amount * rate, 2)

    def get_day_one(self, day: pendulum.DateTime) -> pendulum.Date:
        day = day.subtract(days=1)

        while not self.calendar.is_workday(day):
            day = day.subtract(days=1)

        if self.calendar.is_out_of_range(day):
            raise ValueError("Date {} is out of range".format(day))

        return day
