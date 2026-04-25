"""Parse an IBI Capital 'Sale Of Stock Activity Statement' from extracted PDF text.

IBI Capital ships one PDF per executed sale order. Every PDF has the same
fixed layout; the interesting fields are exposed as ``Label: value`` pairs
or inside one well-identified line (``Total Amount Due to Order N USD
P.PP USD T.TT``). This module uses regex rather than table-extraction
because pdfplumber's text flow scrambles the ``Fees`` block (values appear
before labels) — the labelled totals we care about are easier to read off
the flat text than off the partially-ordered table cells.

This module must not import pdfplumber. That way unit tests can exercise
the parser against anonymized ``.txt`` fixtures without pulling in the
PDF-parsing stack, and the parser stays usable for upstream callers that
feed text from a different source.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import pendulum

from pit38.plugins.normalization import parse_amount


class OrderParseError(ValueError):
    """Raised when a required field is missing from an IBI order PDF text."""


@dataclass(frozen=True)
class ParsedOrder:
    order_number: str
    company: str
    plan: str
    grant_date: pendulum.DateTime
    execution_date: pendulum.DateTime
    shares: int
    sale_price: float
    total_amount: float
    total_fees: float
    price_for_tax: float


# English month names as IBI writes them, e.g. "February 04, 2024".
_DATE_FORMAT = "MMMM DD, YYYY"


def parse_order_report(text: str) -> ParsedOrder:
    """Parse the full text of one IBI order confirmation PDF."""
    shares, sale_price, total_amount = _order_line(text)
    return ParsedOrder(
        order_number=_required(r"Order Number:[ \t]+(\S+)", text, "Order Number"),
        company=_required(r"Company:\s*(.+?)\s*$", text, "Company", flags=re.MULTILINE),
        plan=_required(r"Plan:\s*(.+?)\s*$", text, "Plan", flags=re.MULTILINE),
        grant_date=_date(r"Grant Date:\s+(\w+\s+\d{1,2},\s+\d{4})", text, "Grant Date"),
        execution_date=_date(r"Execution Date:\s+(\w+\s+\d{1,2},\s+\d{4})", text, "Execution Date"),
        shares=shares,
        sale_price=sale_price,
        total_amount=total_amount,
        total_fees=_total_fees(text),
        price_for_tax=_price_for_tax(text),
    )


_ORDER_LINE = re.compile(
    r"Total Amount Due to Order\s+"
    r"(?P<shares>\d+)\s+"
    r"USD\s+(?P<price>[\d,]+\.?\d*)\s+"
    r"USD\s+(?P<total>[\d,]+\.?\d*)"
)


def _order_line(text: str) -> tuple[int, float, float]:
    """Return (shares, sale_price_per_share, total_amount) from the order line."""
    m = _ORDER_LINE.search(text)
    if not m:
        raise OrderParseError("Could not locate 'Total Amount Due to Order' line")
    return (
        int(m.group("shares")),
        parse_amount(m.group("price")),
        parse_amount(m.group("total")),
    )


# The parenthetical note may drift; make it optional so a minor format
# change doesn't break the parser.
_TOTAL_FEES = re.compile(
    r"Total Fees\s+(?:\([^)]*\)\s+)?USD\s+([\d,]+\.?\d*)"
)


def _total_fees(text: str) -> float:
    m = _TOTAL_FEES.search(text)
    if not m:
        raise OrderParseError("Could not locate 'Total Fees' line")
    return parse_amount(m.group(1))


_PRICE_FOR_TAX = re.compile(r"Price For Tax:\s+USD\s+([\d,]+\.?\d*)")


def _price_for_tax(text: str) -> float:
    m = _PRICE_FOR_TAX.search(text)
    if not m:
        raise OrderParseError("Could not locate 'Price For Tax' field")
    return parse_amount(m.group(1))


def _required(pattern: str, text: str, field: str, flags: int = 0) -> str:
    m = re.search(pattern, text, flags)
    if not m:
        raise OrderParseError(f"Could not find '{field}' in PDF text")
    return m.group(1).strip()


def _date(pattern: str, text: str, field: str) -> pendulum.DateTime:
    raw = _required(pattern, text, field)
    try:
        return pendulum.from_format(raw, _DATE_FORMAT)
    except Exception as e:
        raise OrderParseError(f"Could not parse '{field}' date {raw!r}: {e}") from e
