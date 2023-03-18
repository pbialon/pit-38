from typing import List
from loguru import logger

from domain.transactions import Transaction
from domain.stock.profit_calculator import group_transaction_by_company


class Printer:
    def print_stock_transactions_by_company(self, stock_transactions: List[Transaction]):
        grouped_transactions = group_transaction_by_company(stock_transactions)
        for company, transactions in grouped_transactions.items():
            logger.debug(f"Transactions for company: {company}")
            for transaction in transactions:
                logger.debug(f"{transaction}")

    def print_dividends(self, dividends: list):
        logger.debug("Dividends:")
        for dividend in dividends:
            logger.debug(f"{dividend}")

    def print_custody_fees(self, custody_fees: list):
        logger.debug("Custody fees:")
        for fee in custody_fees:
            logger.debug(f"{fee}")
