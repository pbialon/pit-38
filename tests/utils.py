import pendulum

from domain.currency_exchange_service.currencies import FiatValue, Currency
from domain.stock.operations.custody_fee import CustodyFee
from domain.stock.operations.dividend import Dividend
from domain.transactions import AssetValue, Transaction, Action


def btc(amount: float) -> AssetValue:
    return AssetValue(amount, "BTC")


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


def custody_fee(fiat: FiatValue, datetime_str: str) -> CustodyFee:
    parsed_datetime = datetime(datetime_str)
    return CustodyFee(date=parsed_datetime, value=fiat)


def date(date_str: str):
    return pendulum.parse(date_str).date()


def datetime(datetime_str: str):
    return pendulum.parse(datetime_str)


class StubExchanger:
    def exchange(self, date: pendulum.DateTime, fiat_value: FiatValue) -> FiatValue:
        if fiat_value.currency == Currency.DOLLAR:
            return FiatValue(fiat_value.amount * 4.0, Currency.ZLOTY)
        return FiatValue(fiat_value.amount, Currency.ZLOTY)
