import re
from typing import Dict

import pendulum

from pit38.domain.currency_exchange_service.currencies import Currency, FiatValue, parse_currency
from pit38.domain.stock.operations.operation import OperationType
from pit38.domain.transactions import Transaction
from pit38.plugins.normalization import normalize_currency_layout, parse_amount


class RowParser:
    OPERATIONS = {
        "BUY - MARKET": OperationType.BUY,
        "BUY - LIMIT": OperationType.BUY,
        "SELL - MARKET": OperationType.SELL,
        "SELL - LIMIT": OperationType.SELL,
        "DIVIDEND": OperationType.DIVIDEND,
        "CUSTODY FEE": OperationType.SERVICE_FEE,
        "STOCK SPLIT": OperationType.STOCK_SPLIT,
    }

    @classmethod
    def parse(cls, row: Dict) -> Transaction:
        raise NotImplementedError

    @classmethod
    def _fiat_value(cls, row: Dict) -> FiatValue:
        normalized = normalize_currency_layout(row['total amount'])

        # After normalization: "<currency><space><signed_amount>"
        # (both code "USD 529.68" and symbol "$ 529.68" reach the same form)
        match = re.match(r'(\S+)\s+(\S+)$', normalized)
        if not match:
            raise ValueError(f"Cannot parse Total Amount: '{row['total amount']}'")

        currency_str, amount_str = match.groups()
        try:
            currency = parse_currency(currency_str)  # accepts "USD" and "$"
        except Exception:
            raise ValueError(f"Cannot parse Total Amount: '{row['total amount']}'")
        # abs() preserves existing "all fiat values are absolute magnitudes"
        # semantic — callers treat ServiceFee/Dividend/etc. as cost/income
        # regardless of original sign. See #61 for the future refactor that
        # will propagate signed amounts through the domain.
        amount = abs(parse_amount(amount_str))

        cls._validate_currency(row, currency)
        return FiatValue(amount, currency)

    @classmethod
    def _validate_currency(cls, row: Dict, parsed_currency: Currency) -> None:
        if 'currency' in row and row['currency']:
            expected = parse_currency(row['currency'])
            if expected != parsed_currency:
                raise ValueError(
                    f"Currency mismatch: Total Amount implies {parsed_currency}, "
                    f"but Currency column says {expected} (row: {row['total amount']})"
                )

    @classmethod
    def _stock(cls, row: Dict) -> str:
        return row['ticker']

    @classmethod
    def _date(cls, row: dict) -> pendulum.DateTime:
        return pendulum.parse(row['date'])

    @classmethod
    def _operation_type(cls, row: dict) -> OperationType:
        return cls.OPERATIONS.get(row['type'])
