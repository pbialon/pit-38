"""Shared CSV value normalization helpers for broker plugins.

Brokers emit various layouts for the same logical value (amounts,
currencies). This module centralizes rewrite rules so plugins can focus
on broker-specific shape differences rather than re-inventing number
parsing or locale detection.

Used by:
  - pit38.plugins.stock.revolut.row_parser
  - pit38.plugins.stock.etrade.row_parser
"""
import re

from babel.numbers import parse_decimal, NumberFormatError


# Locales tried in order. en_US covers Revolut's historical exports
# (1,234.56); de_DE covers E*Trade's European output (1 234,56 / 1.234,56)
# and forward-compatible Revolut EU exports. If a new broker needs
# something else (e.g. fr_FR with nbsp thousand separator), add it here.
_NUMBER_LOCALES = ("en_US", "de_DE")


def parse_amount(s: str) -> float:
    """Parse a number string, trying configured locales in order.

    Handles thousand/decimal separator combinations:
      "1,234.56"   (en_US) → 1234.56
      "1.234,56"   (de_DE) → 1234.56
      "1 234,56"   (whitespace stripped, de_DE) → 1234.56
      "-0.07"      (en_US) → -0.07
      "-0,07"      (de_DE) → -0.07

    Whitespace (regular space and non-breaking space U+00A0) is stripped
    before parsing. Some brokers use these as thousand separators, but
    CLDR locales don't uniformly recognize them — stripping first keeps
    the code simple.

    Uses babel's strict=True so ambiguous inputs (e.g. "1,317.06"
    under de_DE locale, which would otherwise be misinterpreted as
    1.31706) fail fast instead of being silently mis-parsed. The
    locale chain then tries the next locale.

    Returns a float for compatibility with existing FiatValue.amount.
    When #61 migrates to Decimal, this can return babel's Decimal
    directly (it already does internally).

    Raises ValueError if no configured locale can parse the input.
    """
    cleaned = s.replace("\xa0", "").replace(" ", "")
    for locale in _NUMBER_LOCALES:
        try:
            return float(parse_decimal(cleaned, locale=locale, strict=True))
        except NumberFormatError:
            continue
    raise ValueError(
        f"Cannot parse amount in any supported locale "
        f"({', '.join(_NUMBER_LOCALES)}): {s!r}"
    )


def normalize_currency_layout(raw: str) -> str:
    """Rewrite a currency+amount string to canonical layout.

    Canonical form: ``<currency><single space><signed_amount>``

    Input variants collected from real Revolut and E*Trade exports:

      ==============  ================
      input           → canonical
      ==============  ================
      "USD 529.68"    → "USD 529.68"   (already canonical)
      "-USD 529.68"   → "USD -529.68"  (move sign past currency code)
      "USD -0.07"     → "USD -0.07"    (already; #33 @inobrevi case)
      "$500"          → "$ 500"        (insert space)
      "-$529.68"      → "$ -529.68"    (move sign + insert space)
      "$-0.07"        → "$ -0.07"      (insert space)
      "€250.00"       → "€ 250.00"     (insert space)
      "$25 001,75"    → "$ 25 001,75"  (only insert space; amount preserved)

    Sign stays attached to the amount side. parse_amount() handles the
    signed number per-locale.

    Format-only: does NOT strip the sign and does NOT touch the inside
    of the amount (digits/separators). That's parse_amount's job.
    """
    # Move leading minus past currency code: "-USD X" → "USD -X"
    raw = re.sub(r"^-([A-Z]{3}\s+)", r"\1-", raw)
    # Move leading minus past currency symbol + insert space: "-$X" → "$ -X"
    raw = re.sub(r"^-([^\w\s])", r"\1 -", raw)
    # Insert space between currency symbol and amount: "$X" → "$ X"
    # Currency codes already have a space after them (3-letter codes are
    # word characters, so the regex starts with [^\w\s] = symbol only).
    raw = re.sub(r"^([^\w\s])(?=[-\d])", r"\1 ", raw)
    return raw
