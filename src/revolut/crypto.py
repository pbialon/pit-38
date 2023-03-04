from collections import defaultdict
from src.exchange.exchanger import Exchanger
import pendulum, json
from typing import List, Tuple

from src.utils import YEAR, InvalidYearException

CRYPTO_TRADES_FILENAME = "/Users/pbialon/workbench/pit/resources/crypto_transactions.json"


class InvalidCurrencyException(Exception):
    pass


class CryptocurrencyExchange:
    TYPE = "EXCHANGE"

    def __init__(
            self,
            currency: str,
            amount_in_dollars: float,
            amount_in_pln: float,
            quantity: float,
            action: str,
            date: pendulum.DateTime,
    ):
        self.currency = currency
        self.amount_in_dollars = amount_in_dollars
        self.amount_in_pln = amount_in_pln
        self.quantity = quantity
        self.action = action
        self.date = date

    def __str__(self):
        return f"{self.date.format('DD.MM.YYYY')}: {self.action} {self.quantity} {self.currency} => {self.amount_in_pln} zł"


class ExchangeBuilder:
    COMPLETED_STATE = "COMPLETED"

    DIRECTION = "buy"

    def __init__(self, exchanger: Exchanger):
        self.exchanger = exchanger

    def _get_datetime_from_timestamp(
            self, transaction_data: dict, key: str = "completedDate"
    ) -> pendulum.DateTime:
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


def read_revolut_data_from_file(filename: str) -> list:
    with open(filename, "r") as file:
        data = json.load(file)
    return data["items"]


def prepare_data() -> List[CryptocurrencyExchange]:
    exchanger = Exchanger()
    transactions = read_revolut_data_from_file(CRYPTO_TRADES_FILENAME)
    crypto_transactions = defaultdict(list)
    builder = ExchangeBuilder(exchanger)
    for transaction in transactions:
        if transaction.get("type") == CryptocurrencyExchange.TYPE:
            try:
                ct = builder.build_crypto(transaction)
            except InvalidCurrencyException as e:
                print(e)
                continue
            except InvalidYearException:
                continue

            if not ct:
                continue
            crypto_transactions[ct.currency].append(ct)
    return crypto_transactions


def calculate_income_and_cost(desired_currency: str = "") -> Tuple[float, float]:
    transactions = prepare_data()
    income = 0
    cost = 0
    for currency, transactions in transactions.items():
        if desired_currency and currency != desired_currency:
            continue
        for transaction in transactions:
            if transaction.amount_in_pln < 0:
                cost += transaction.amount_in_pln
            else:
                income += transaction.amount_in_pln
    return income, cost


def print_transactions():
    transactions = prepare_data()
    for currency, transactions in transactions.items():
        print(f"{currency}:")
        for transaction in transactions:
            print(f"\t{transaction}")


if __name__ == "__main__":
    # print_transactions()
    for currency in ("BTC", "ETH", "LTC", "XLM", "DOGE", "ADA", "BCH", ""):
        income, cost = calculate_income_and_cost(currency)
        currency = currency or "TOTAL"
        print(f"{currency}: income: {income} cost: {cost}")
