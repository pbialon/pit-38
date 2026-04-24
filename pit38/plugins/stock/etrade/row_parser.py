import re

from loguru import logger

from pit38.domain.currency_exchange_service.currencies import Currency, FiatValue
from pit38.plugins.normalization import normalize_currency_layout, parse_amount


class FiatValueParser:
    SYMBOL_TO_CURRENCY = {
        "$": Currency.DOLLAR,
        "€": Currency.EURO,
    }

    @classmethod
    def parse(cls, raw_fiat_value: str) -> FiatValue:
        logger.debug(f"Parsing fiat value: {raw_fiat_value}")

        normalized = normalize_currency_layout(raw_fiat_value)
        # After normalization: "<symbol><space><amount_possibly_with_inner_whitespace>"
        # Split on FIRST whitespace only — amount may legitimately contain
        # space (as EU thousand separator) that parse_amount strips.
        match = re.match(r'(\S+)\s+(.+)$', normalized)
        if not match:
            raise ValueError(f"Cannot parse fiat value: '{raw_fiat_value}'")

        symbol, amount_str = match.groups()
        currency = cls.SYMBOL_TO_CURRENCY.get(symbol)
        if currency is None:
            raise ValueError(
                f"Unknown currency symbol: {symbol!r} in {raw_fiat_value!r}"
            )
        # abs() preserves existing absolute-magnitude semantic — see Revolut
        # parser for rationale. Will change when #61 propagates signed amounts.
        amount = abs(parse_amount(amount_str))
        return FiatValue(amount=amount, currency=currency)
