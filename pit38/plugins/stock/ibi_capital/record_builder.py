"""Turn a ParsedOrder into domain records that the standardized loader consumes.

Each IBI order yields:

* ``BUY`` transaction dated at the grant day — synthetic, because IBI order
  reports do not include the original basis. We encode the Polish tax
  interpretation (KIS line) where RSU cost basis is 0 and ESPP cost basis
  is the discounted purchase price, via ``Price For Tax``.
* ``SELL`` transaction dated at the execution day, using ``Total Amount
  Due to Order`` as gross proceeds.
* ``ServiceFee`` dated at the execution day (if non-zero).

BUY uses 09:00:00 and SELL uses 10:00:00 so that FIFO matching stays
deterministic when ``Grant Date == Execution Date`` (possible for same-day
equity events).
"""
from __future__ import annotations

from pit38.domain.currency_exchange_service.currencies import Currency, FiatValue
from pit38.domain.stock.operations.service_fee import ServiceFee
from pit38.domain.transactions import Action, AssetValue, Transaction

from .order_parser import ParsedOrder

_BUY_TIME = {"hour": 9, "minute": 0, "second": 0}
_SELL_TIME = {"hour": 10, "minute": 0, "second": 0}


def build_records(
    order: ParsedOrder,
    ticker: str,
) -> tuple[list[Transaction], list[ServiceFee]]:
    """Emit BUY + SELL transactions and a ServiceFee (if fees > 0).

    The shares count and ticker are identical for BUY and SELL; the pair
    represents one acquisition + one liquidation of the same position.
    """
    shares = order.shares
    asset = AssetValue(amount=float(shares), asset_name=ticker)

    buy = Transaction(
        asset=asset,
        fiat_value=FiatValue(
            amount=round(shares * order.price_for_tax, 2),
            currency=Currency.DOLLAR,
        ),
        action=Action.BUY,
        date=order.grant_date.set(**_BUY_TIME),
    )

    sell = Transaction(
        asset=asset,
        fiat_value=FiatValue(amount=order.total_amount, currency=Currency.DOLLAR),
        action=Action.SELL,
        date=order.execution_date.set(**_SELL_TIME),
    )

    fees: list[ServiceFee] = []
    if order.total_fees > 0:
        fees.append(
            ServiceFee(
                date=order.execution_date.set(**_SELL_TIME),
                value=FiatValue(amount=order.total_fees, currency=Currency.DOLLAR),
            )
        )

    return [buy, sell], fees
