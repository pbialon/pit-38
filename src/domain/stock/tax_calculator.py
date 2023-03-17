from collections import defaultdict
from typing import List, Dict

from domain.transactions import Transaction


def group_stock_trade_by_company(stock_transactions: List[Transaction]) -> Dict[str, List[Transaction]]:
    grouped_transactions = defaultdict(list)
    for transaction in stock_transactions:
        company_name = transaction.asset.asset_name
        grouped_transactions[company_name].append(transaction)
    return grouped_transactions
