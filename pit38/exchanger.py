from pit38.domain.calendar_service.calendar import Calendar
from pit38.domain.currency_exchange_service.exchange_rates_provider import ExchangeRatesProvider
from pit38.domain.currency_exchange_service.exchanger import Exchanger


def create_exchanger() -> Exchanger:
    calendar = Calendar()
    rates_provider = ExchangeRatesProvider()
    return Exchanger(rates_provider, calendar)
