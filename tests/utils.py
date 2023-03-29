import pendulum

from domain.currency_exchange_service.currencies import FiatValue, Currency
from domain.transactions import AssetValue, Transaction, Action


def btc(amount):
    return AssetValue(amount, "BTC")


def usd(amount):
    return FiatValue(amount, Currency.DOLLAR)


def zl(amount):
    return FiatValue(amount, Currency.ZLOTY)


def buy(crypto, fiat, date):
    parsed_date = pendulum.parse(date)
    return Transaction(date=parsed_date, asset=crypto, fiat_value=fiat, action=Action.BUY)


def sell(crypto, fiat, date):
    parsed_date = pendulum.parse(date)
    return Transaction(date=parsed_date, asset=crypto, fiat_value=fiat, action=Action.SELL)


class StubExchanger:
    def exchange(self, date: pendulum.DateTime, fiat_value: FiatValue) -> FiatValue:
        if fiat_value.currency == Currency.DOLLAR:
            return FiatValue(fiat_value.amount * 4.0, Currency.ZLOTY)
        return FiatValue(fiat_value.amount, Currency.ZLOTY)
