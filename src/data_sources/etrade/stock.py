import csv
from typing import List
from loguru import logger
import pandas as pd
import pendulum

from data_sources.etrade.fiat_value_parser import FiatValueParser
from domain.transactions.action import Action
from domain.transactions.asset import AssetValue
from domain.transactions.transaction import Transaction

FILEPATH = "~/Downloads/Etrade.csv"


def get_stock_data(file_path):
    """
    Get stock data from the csv file
    """
    transactions = []
    logger.info(f"Reading transactions from {file_path}...")
    with open(file_path, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        for row in reader:
            transactions.extend(parse_row(row))

    logger.info(f"Parsed {len(transactions)} transactions")
    return transactions


def parse_row(row: pd.Series) -> List[Transaction]:
    """
    Parse a row from the DataFrame into a Transaction object
    """
    buy = Transaction(
        asset=AssetValue(amount=float(row["Qty."]), asset_name=row["Symbol"]),
        fiat_value=FiatValueParser.parse(row["Acquisition Cost"]),
        action=Action.BUY,
        date=pendulum.parse(str(row["Date Acquired"]), strict=False),
    )
    logger.debug(f"Parsed buy transaction: {buy}")

    sell = Transaction(
        asset=AssetValue(amount=float(row["Qty."]), asset_name=row["Symbol"]),
        fiat_value=FiatValueParser.parse(row["Total Proceeds"]),
        action=Action.SELL,
        date=pendulum.parse(str(row["Date Sold"]), strict=False),
    )
    logger.debug(f"Parsed sell transaction: {sell}")

    return [buy, sell]
