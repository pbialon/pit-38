import pendulum

from domain.currency_exchange_service.currencies import FiatValue, Currency
from domain.transactions import AssetValue, Transaction, Action


def btc(amount: float) -> AssetValue:
    return AssetValue(amount, "BTC")


def usd(amount: float) -> FiatValue:
    return FiatValue(amount, Currency.DOLLAR)


def zl(amount: float) -> FiatValue:
    return FiatValue(amount, Currency.ZLOTY)


def buy(crypto, fiat: FiatValue, datetime_str: str) -> Transaction:
    parsed_datetime = pendulum.parse(datetime_str)
    return Transaction(date=parsed_datetime, asset=crypto, fiat_value=fiat, action=Action.BUY)


def sell(crypto, fiat: FiatValue, datetime_str: str) -> Transaction:
    parsed_datetime = pendulum.parse(datetime_str)
    return Transaction(date=parsed_datetime, asset=crypto, fiat_value=fiat, action=Action.SELL)


def date(date_str: str):
    return pendulum.parse(date_str).date()


class StubExchanger:
    def exchange(self, date: pendulum.DateTime, fiat_value: FiatValue) -> FiatValue:
        if fiat_value.currency == Currency.DOLLAR:
            return FiatValue(fiat_value.amount * 4.0, Currency.ZLOTY)
        return FiatValue(fiat_value.amount, Currency.ZLOTY)
