import json
import pendulum
from typing import List

from src.utils import YEAR, InvalidYearException
from domain.currency_exchange_service.exchanger import Exchanger

STOCK_TRADES_FILENAME = "/Users/pbialon/workbench/pit/resources/stock_transactions.json"


class CustodyFee:
    TYPE = "CUSTODY_FEES"

    def __init__(
            self, amount_in_dollars: float, amount_in_pln: float, date: pendulum.DateTime
    ):
        self.amount_in_dollars = amount_in_dollars
        self.amount_in_pln = amount_in_pln
        self.date = date

    def __str__(self):
        return f"{self.date.format('DD.MM.YYYY')}: {self.amount_in_pln} zł"


class StockTrade:
    TYPE = "TRADE"

    def __init__(
            self,
            date: pendulum.DateTime,
            amount_in_dollars: float,
            amount_in_pln: float,
            quantity: float,
            fee: float,
            company: str,
            action: str,
    ):
        self.date = date
        self.amount_in_dollars = amount_in_dollars
        self.amount_in_pln = amount_in_pln
        self.quantity = quantity
        self.fee = fee
        self.company = company
        self.action = action  # (bought or sold)

    def price(self):
        return self.amount_in_pln / self.quantity

    def __str__(self):
        return f"{self.date.format('DD.MM.YYYY')}: {self.amount_in_pln} zł\t {self.action} {self.quantity} of {self.company} "


class Dividend:
    TYPE = "DIVIDENDS"

    def __init__(
            self, date: pendulum.DateTime, amount_in_dollars: float, amount_in_pln: float
    ):
        self.date = date
        self.amount_in_dollars = amount_in_dollars
        self.amount_in_pln = amount_in_pln

    def __str__(self):
        return f"{self.date.format('DD.MM.YYYY')}: {self.amount_in_pln} zł"


class TransactionBuilder:
    COMPLETED_STATE = "COMPLETED"

    def __init__(self, exchanger: Exchanger):
        self.exchanger = exchanger

    def _calculate_fee(self, transaction_data: dict):
        fees = sum(fee["amount"]["amount"] / 100 for fee in transaction_data["fees"])
        commissions = 0
        try:
            commissions = (
                    transaction_data["commission"]["instrumentCurrencyValue"]["amount"]
                    / 100
            )
        except:
            pass

        return fees + commissions

    def _get_datetime_from_timestamp(
            self, transaction_data: dict, key: str = "completedAt"
    ) -> pendulum.DateTime:
        datetime = pendulum.from_timestamp(
            transaction_data[key] / 1000, tz="Europe/Warsaw"
        )
        if datetime.year != YEAR:
            raise InvalidYearException(datetime.year)
        return datetime

    def build_stock_trade(self, transaction_data: dict) -> StockTrade:
        if transaction_data["state"] != TransactionBuilder.COMPLETED_STATE:
            return None

        try:
            date = self._get_datetime_from_timestamp(transaction_data)
        except InvalidYearException:
            return None

        amount_in_dollars = transaction_data["total"]["amount"] / 100
        amount_in_pln = self.exchanger.exchange(date, amount_in_dollars)

        return StockTrade(
            date,
            amount_in_dollars,
            amount_in_pln,
            float(transaction_data["executedQuantity"]),
            self._calculate_fee(transaction_data),
            transaction_data["symbol"],
            transaction_data["side"],
        )

    def build_custody_fee(self, transaction_data: dict) -> CustodyFee:
        if transaction_data["state"] != TransactionBuilder.COMPLETED_STATE:
            return None

        try:
            date = self._get_datetime_from_timestamp(transaction_data)
        except InvalidYearException:
            return None

        amount_in_dollars = transaction_data["value"]["amount"] / 100
        amount_in_pln = self.exchanger.exchange(date, amount_in_dollars)
        return CustodyFee(amount_in_dollars, amount_in_pln, date)

    def build_dividend(self, transaction_data: dict) -> Dividend:
        if transaction_data["state"] != TransactionBuilder.COMPLETED_STATE:
            return None

        try:
            date = self._get_datetime_from_timestamp(transaction_data, "createdAt")
        except InvalidYearException:
            return None

        amount_in_dollars = transaction_data["value"]["amount"] / 100
        amount_in_pln = self.exchanger.exchange(date, amount_in_dollars)
        return Dividend(date, amount_in_dollars, amount_in_pln)


def read_revolut_data_from_file(filename: str):
    with open(filename, "r") as f:
        data = json.load(f)
    return data["items"]


def prepare_data():
    exchanger = Exchanger()
    transactions = read_revolut_data_from_file(STOCK_TRADES_FILENAME)
    stock_transactions = []
    custody_fees = []
    dividends = []
    builder = TransactionBuilder(exchanger)
    for transaction in transactions:
        if transaction.get("type") == StockTrade.TYPE:
            st = builder.build_stock_trade(transaction)
            if not st:
                continue
            stock_transactions.append(st)
        elif transaction.get("type") == CustodyFee.TYPE:
            cf = builder.build_custody_fee(transaction)
            if not cf:
                continue
            custody_fees.append(cf)
        elif transaction.get("type") == Dividend.TYPE:
            d = builder.build_dividend(transaction)
            if not d:
                continue
            dividends.append(d)

    return stock_transactions, custody_fees, dividends


def group_stock_trade_by_company(stock_transactions: List[StockTrade]):
    grouped_transactions = {}
    for transaction in stock_transactions:
        if transaction.company not in grouped_transactions:
            grouped_transactions[transaction.company] = []
        grouped_transactions[transaction.company].append(transaction)
    return grouped_transactions


class Printer:
    def print_stock_transactions_by_company(self, stock_transactions: list):
        grouped_transactions = group_stock_trade_by_company(stock_transactions)
        for company, transactions in grouped_transactions.items():
            print(f"{company}:")
            for transaction in transactions:
                print(f"\t{transaction}")
            print("")

    def print_dividends(self, dividends: list):
        for dividend in dividends:
            print(f"{dividend}")
        print("")

    def print_custody_fees(self, custody_fees: list):
        for fee in custody_fees:
            print(f"{fee}")
        print("")


class TaxCalculatorPerCompany:
    def __init__(self, company: str):
        self.company = company

    def calculate_taxes_for_company(self, transactions: List[StockTrade]):
        # sort transactions by date
        transactions.sort(key=lambda x: x.date)
        fifo_queue: List[StockTrade] = []
        cost, income = 0, 0
        for transaction in transactions:
            # print(transactions)
            if transaction.action == "BUY":
                fifo_queue.append((transaction, transaction.quantity))
                continue

            quantity = transaction.quantity

            while quantity > 0.00000001:
                oldest_transaction, oldest_transaction_quantity = (
                    fifo_queue[0][0],
                    fifo_queue[0][1],
                )
                if oldest_transaction_quantity > quantity:
                    cost += oldest_transaction.price() * quantity
                    income += transaction.price() * quantity
                    fifo_queue[0] = (
                        oldest_transaction,
                        oldest_transaction_quantity - transaction.quantity,
                    )
                    break
                cost += oldest_transaction.price() * oldest_transaction_quantity
                income += transaction.price() * oldest_transaction_quantity
                fifo_queue.pop(0)
                quantity -= oldest_transaction_quantity
        return cost, income


def taxes():
    stock_transactions, custody_fees, dividends = prepare_data()
    total_revenue, total_cost, total_income = 0, 0, 0
    for company, transactions in group_stock_trade_by_company(
            stock_transactions
    ).items():
        print(f"{company}:")
        calc = TaxCalculatorPerCompany(company)
        cost, income = calc.calculate_taxes_for_company(transactions)
        total_cost += cost
        total_income += income
        total_revenue += income - cost
        print(f"\tcost: {round(cost, 2)}\tincome: {round(income, 2)}")
        print(f"\trevenue: {round(income - cost, 2)}")
        print("")
        print("")
    print(
        "total cost:",
        round(total_cost, 2),
        "total income:",
        round(total_income, 2),
        "total revenue:",
        round(total_revenue, 2),
    )


if __name__ == "__main__":
    taxes()
    # Printer().print_dividends(prepare_data()[-1])
