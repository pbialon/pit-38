import pendulum

from exchange.exchanger import Exchanger
from revolut.crypto.invalid_currency_exception import InvalidCurrencyException
from utils import InvalidYearException, YEAR


class CryptocurrencyExchange:
    TYPE = "EXCHANGE"

    def __init__(self,
                 currency: str,
                 amount_in_dollars: float,
                 amount_in_pln: float,
                 quantity: float,
                 action: str,
                 date: pendulum.DateTime):
        self.currency = currency
        self.amount_in_dollars = amount_in_dollars
        self.amount_in_pln = amount_in_pln
        self.quantity = quantity
        self.action = action
        self.date = date

    def __str__(self):
        return f"{self.date.format('DD.MM.YYYY')}: {self.action} {self.quantity} {self.currency} " \
               f"=> {self.amount_in_pln} zł"


class ExchangeBuilder:
    COMPLETED_STATE = "COMPLETED"

    DIRECTION = "buy"

    def __init__(self, exchanger: Exchanger):
        self.exchanger = exchanger

    def _get_datetime_from_timestamp(self,
                                     transaction_data: dict,
                                     key: str = "completedDate") -> pendulum.DateTime:
        datetime = pendulum.from_timestamp(
            transaction_data[key] / 1000, tz="Europe/Warsaw"
        )

        if datetime.year != YEAR:
            raise InvalidYearException(datetime.year)
        return datetime

    def _handle_buy(self, transaction_data: dict, date: pendulum.DateTime):
        crypto_name = transaction_data["currency"]
        quantity = transaction_data["amount"] / 10 ** 8
        if transaction_data["counterpart"]["currency"] == "USD":
            amount_in_dollars = transaction_data["counterpart"]["amount"] / 100
            amount_in_pln = self.exchanger.exchange(date, amount_in_dollars)

        elif transaction_data["counterpart"]["currency"] == "PLN":
            amount_in_pln = transaction_data["counterpart"]["amount"] / 100
            amount_in_dollars = None
        else:
            raise InvalidCurrencyException(transaction_data)

        return CryptocurrencyExchange(
            crypto_name, amount_in_dollars, amount_in_pln, quantity, "bought", date
        )

    def _handle_sell(self, transaction_data: dict, date: pendulum.DateTime):
        quantity = transaction_data["counterpart"]["amount"] / 10 ** 8
        crypto_name = transaction_data["counterpart"]["currency"]
        if transaction_data["currency"] == "USD":
            amount_in_dollars = transaction_data["amount"] / 100
            amount_in_pln = self.exchanger.exchange(date, amount_in_dollars)
        elif transaction_data["currency"] == "PLN":
            amount_in_pln = transaction_data["amount"] / 100
            amount_in_dollars = None
        else:
            raise InvalidCurrencyException(transaction_data)

        return CryptocurrencyExchange(
            crypto_name, amount_in_dollars, amount_in_pln, quantity, "sold", date
        )

    def build_crypto(self, transaction_data: dict) -> CryptocurrencyExchange:
        if transaction_data["state"] != self.COMPLETED_STATE:
            return None
        date = self._get_datetime_from_timestamp(transaction_data)

        if transaction_data["direction"] != self.DIRECTION:
            return None

        if transaction_data["currency"] in ("PLN", "USD"):
            return self._handle_sell(transaction_data, date)
        return self._handle_buy(transaction_data, date)
