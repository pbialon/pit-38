import pendulum

from pit38.domain.currency_exchange_service.currencies import FiatValue, Currency
from pit38.domain.stock.operations.service_fee import ServiceFee
from pit38.domain.stock.operations.dividend import Dividend
from pit38.domain.stock.operations.stock_split import StockSplit
from pit38.domain.transactions import AssetValue, Transaction, Action


def btc(amount: float) -> AssetValue:
    return AssetValue(amount, "BTC")


def eth(amount: float) -> AssetValue:
    return AssetValue(amount, "ETH")


def apple(amount: float) -> AssetValue:
    return AssetValue(amount, "AAPL")


def amazon(amount: float) -> AssetValue:
    return AssetValue(amount, "AMZN")

def meta(amount: float) -> AssetValue:
    return AssetValue(amount, "META")


def google(amount: float) -> AssetValue:
    return AssetValue(amount, "GOOGL")


def usd(amount: float) -> FiatValue:
    return FiatValue(amount, Currency.DOLLAR)


def zl(amount: float) -> FiatValue:
    return FiatValue(amount, Currency.ZLOTY)


def buy(asset: AssetValue, fiat: FiatValue, datetime_str: str) -> Transaction:
    parsed_datetime = datetime(datetime_str)
    return Transaction(date=parsed_datetime, asset=asset, fiat_value=fiat, action=Action.BUY)


def sell(asset: AssetValue, fiat: FiatValue, datetime_str: str) -> Transaction:
    parsed_datetime = datetime(datetime_str)
    return Transaction(date=parsed_datetime, asset=asset, fiat_value=fiat, action=Action.SELL)


def dividend(fiat: FiatValue, datetime_str: str) -> Dividend:
    parsed_datetime = datetime(datetime_str)
    return Dividend(date=parsed_datetime, value=fiat)


def service_fee(fiat: FiatValue, datetime_str: str) -> ServiceFee:
    return ServiceFee(
        date=pendulum.parse(datetime_str),
        value=fiat
    )


def date(date_str: str):
    return pendulum.parse(date_str).date()


def datetime(datetime_str: str):
    return pendulum.parse(datetime_str)


class StubExchanger:
    def exchange(self, date: pendulum.DateTime, fiat_value: FiatValue) -> FiatValue:
        if fiat_value.currency == Currency.DOLLAR:
            return FiatValue(fiat_value.amount * 4.0, Currency.ZLOTY)
        return FiatValue(fiat_value.amount, Currency.ZLOTY)


class DateAwareExchanger:
    """Exchanger that returns different rates based on the date's month."""
    def __init__(self, rates: dict[str, float]):
        self.rates = rates

    def exchange(self, date: pendulum.DateTime, fiat_value: FiatValue) -> FiatValue:
        date_key = date.format("YYYY-MM-DD") if hasattr(date, 'format') else str(date)
        for key, rate in self.rates.items():
            if date_key.startswith(key):
                return FiatValue(round(fiat_value.amount * rate, 2), Currency.ZLOTY)
        return FiatValue(fiat_value.amount * 4.0, Currency.ZLOTY)
