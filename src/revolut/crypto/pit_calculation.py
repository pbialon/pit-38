import json
from collections import defaultdict
from typing import List, Tuple

from exchange.exchanger import Exchanger
from revolut.crypto.exchange import CryptocurrencyExchange, ExchangeBuilder
from revolut.crypto.invalid_currency_exception import InvalidCurrencyException
from utils import InvalidYearException

CRYPTO_TRADES_FILENAME = "/Users/pbialon/workbench/pit/resources/crypto_transactions.json"


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
