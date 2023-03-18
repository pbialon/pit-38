import pendulum

from domain.calendar_service.calendar import Calendar, today
from domain.currency_exchange_service.exchange_rates_provider import ExchangeRatesProvider
from domain.currency_exchange_service.exchanger import Exchanger

DISTANT_PAST = pendulum.Date(2015, 1, 1)


def create_exchanger() -> Exchanger:
    calendar = Calendar()
    rates_provider = ExchangeRatesProvider(DISTANT_PAST, today())
    return Exchanger(rates_provider, calendar)
